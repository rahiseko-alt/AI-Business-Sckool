from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal, InvalidOperation
from enum import StrEnum
from typing import Any

from grading.domain.enums import ValueKind


class Policy(StrEnum):
    """数値でない値（未提出・欠席など）をどう扱うか。平均補完などは存在しない。"""

    SCORE_ZERO = "SCORE_ZERO"   # 0点として数える
    EXCLUDE = "EXCLUDE"         # その項目を分子・分母の両方から除く


class Rounding(StrEnum):
    NONE = "NONE"
    HALF_UP_INT = "HALF_UP_INT"
    DOWN_INT = "DOWN_INT"

    def apply(self, value: Decimal) -> Decimal:
        if self == Rounding.NONE:
            return value
        mode = ROUND_HALF_UP if self == Rounding.HALF_UP_INT else ROUND_DOWN
        return value.quantize(Decimal(1), rounding=mode)


class RuleError(ValueError):
    def __init__(self, subject: str, problems: list[str]):
        super().__init__(f"{subject}: " + " / ".join(problems))
        self.subject = subject
        self.problems = problems


@dataclass(frozen=True)
class Component:
    name: str
    weight: Decimal
    items: tuple[str, ...]


@dataclass(frozen=True)
class SubjectRule:
    subject: str
    rule_ref: str                                   # 根拠（資料の source_id か回答の decision_id）
    components: tuple[Component, ...]
    max_scores: Mapping[str, Decimal]
    grade_thresholds: tuple[tuple[str, Decimal], ...]  # 下限の降順。最後は必ず 0
    rounding: Rounding
    markers: Mapping[str, ValueKind]
    value_policies: Mapping[ValueKind, Policy]

    def grade_for(self, total: Decimal) -> str:
        for grade, minimum in self.grade_thresholds:
            if total >= minimum:
                return grade
        raise AssertionError("thresholds always end with 0")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SubjectRule":
        subject = str(data.get("subject") or "").strip()
        problems: list[str] = []
        if not subject:
            problems.append("科目名が無い")
        rule_ref = str(data.get("rule_ref") or "").strip()
        if not rule_ref:
            problems.append("ルールの根拠（資料または回答）が無い")

        components = _components(data.get("components"), problems)
        max_scores = _max_scores(data.get("max_scores"), components, problems)
        thresholds = _thresholds(data.get("grade_thresholds"), problems)
        rounding = _enum(Rounding, data.get("rounding"), "端数処理", problems)
        markers = {str(k): v for k, v in _enum_map(ValueKind, data.get("markers"), "記号", problems).items()}
        policies = {
            ValueKind(k): v for k, v in _enum_map(Policy, data.get("value_policies"), "値の扱い", problems).items()
            if k in ValueKind.__members__
        }
        for k in (data.get("value_policies") or {}):
            if k not in ValueKind.__members__ or k in (ValueKind.NUMBER, ValueKind.ZERO, ValueKind.UNKNOWN):
                problems.append(f"値の扱いを決められない種類: {k}")

        if problems:
            raise RuleError(subject or "(科目不明)", problems)
        return cls(subject, rule_ref, components, max_scores, thresholds, rounding, markers, policies)


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        d = Decimal(str(value))
    except InvalidOperation:
        return None
    return d if d.is_finite() else None


def _components(raw: Any, problems: list[str]) -> tuple[Component, ...]:
    if not raw:
        problems.append("評価項目と配点が無い")
        return ()
    result, seen_items, total = [], set(), Decimal(0)
    for c in raw:
        name, weight, items = c.get("name"), _decimal(c.get("weight")), tuple(c.get("items") or ())
        if not name or weight is None or weight <= 0 or not items:
            problems.append(f"評価項目の定義が不完全: {c}")
            continue
        for item in items:
            if item in seen_items:
                problems.append(f"項目 {item} が複数の評価項目に含まれる")
            seen_items.add(item)
        total += weight
        result.append(Component(str(name), weight, items))
    if result and total != 100:
        problems.append(f"配点の合計が100ではない（{total}）")
    return tuple(result)


def _max_scores(raw: Any, components: Iterable[Component], problems: list[str]) -> dict[str, Decimal]:
    raw = raw or {}
    result = {}
    for c in components:
        for item in c.items:
            value = _decimal(raw.get(item))
            if value is None or value <= 0:
                problems.append(f"項目 {item} の満点が無い")
            else:
                result[item] = value
    return result


def _thresholds(raw: Any, problems: list[str]) -> tuple[tuple[str, Decimal], ...]:
    if not raw:
        problems.append("ABCDE等の評価基準が無い")
        return ()
    pairs = []
    for entry in raw:
        grade, minimum = (entry[0], _decimal(entry[1])) if len(entry) == 2 else (None, None)
        if not grade or minimum is None or not 0 <= minimum <= 100:
            problems.append(f"評価基準の定義が不正: {entry}")
            continue
        pairs.append((str(grade), minimum))
    grades, minimums = [g for g, _ in pairs], [m for _, m in pairs]
    if len(set(grades)) != len(grades) or len(set(minimums)) != len(minimums):
        problems.append("評価基準の記号または下限が重複している")
    if pairs and min(minimums) != 0:
        problems.append("評価基準が0点を含んでいない")
    return tuple(sorted(pairs, key=lambda p: p[1], reverse=True))


def _enum(kind, raw: Any, label: str, problems: list[str]):
    if raw is None:
        problems.append(f"{label}の方法が無い")
        return None
    try:
        return kind(raw)
    except ValueError:
        problems.append(f"{label}の方法が不明: {raw}")
        return None


def _enum_map(kind, raw: Any, label: str, problems: list[str]) -> dict:
    result = {}
    for k, v in (raw or {}).items():
        try:
            result[k] = kind(v)
        except ValueError:
            problems.append(f"{label}の定義が不明: {k} → {v}")
    return result


class RuleBook:
    """科目名で引くだけ。見つからなければ KeyError。似た科目への読み替えはしない。"""

    def __init__(self, rules: Iterable[SubjectRule]):
        self._rules: dict[str, SubjectRule] = {}
        for rule in rules:
            if rule.subject in self._rules:
                raise ValueError(f"two rules for subject {rule.subject}")
            self._rules[rule.subject] = rule

    def get(self, subject: str) -> SubjectRule:
        return self._rules[subject]

    def subjects(self) -> list[str]:
        return list(self._rules)
