from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from fractions import Fraction

from grading.domain.enums import DataStatus, IssueType, ValueKind
from grading.normalization import ParsedValue
from grading.rules import Policy, SubjectRule

_NUMERIC = (ValueKind.NUMBER, ValueKind.ZERO)


@dataclass(frozen=True)
class ItemValue:
    item: str
    value: ParsedValue
    evidence_id: int | str
    status: DataStatus          # 名寄せ・抽出の段階で付いた状態


@dataclass(frozen=True)
class CalcProblem:
    issue_type: IssueType
    item: str | None
    detail: str


@dataclass(frozen=True)
class ComponentScore:
    component: str
    score: Fraction             # 計算は厳密な有理数で行い、丸めは合計に1回だけ
    weight: Fraction
    evidence_ids: tuple[int | str, ...]


@dataclass(frozen=True)
class SubjectResult:
    student_key: str
    subject: str
    components: tuple[ComponentScore, ...]
    unrounded_total: Fraction
    total: Fraction
    grade: str
    rule_ref: str
    status: DataStatus


def as_list(values: Mapping[str, ItemValue] | Iterable[ItemValue]) -> list[ItemValue]:
    if isinstance(values, Mapping):
        for key, v in values.items():
            if key != v.item:
                raise ValueError(f"key {key!r} does not match item {v.item!r}")
        return list(values.values())
    return list(values)


def calculate(
    student_key: str, rule: SubjectRule, values: Mapping[str, ItemValue] | Iterable[ItemValue]
) -> SubjectResult | list[CalcProblem]:
    """1学生1科目の得点を計算する。問題があれば得点は作らず、見つかった問題をすべて返す。"""
    values = as_list(values)
    problems: list[CalcProblem] = []
    known = {item for c in rule.components for item in c.items}
    by_item: dict[str, ItemValue] = {}
    for v in values:
        if v.item not in known:
            problems.append(CalcProblem(IssueType.ITEM_UNKNOWN, v.item, "採点ルールに無い項目"))
        elif v.item in by_item:
            problems.append(CalcProblem(IssueType.DATA_CONFLICT, v.item,
                                        f"同じ項目の値が複数ある: {by_item[v.item].evidence_id} / {v.evidence_id}"))
        else:
            by_item[v.item] = v

    components = []
    for c in rule.components:
        earned, possible, evidence, failed = Fraction(0), Fraction(0), [], False
        for item in c.items:
            v = by_item.get(item)
            if v is None:
                problems.append(CalcProblem(IssueType.INCOMPLETE, item, "値が無い"))
                failed = True
                continue
            evidence.append(v.evidence_id)
            if v.status == DataStatus.BLOCKED:
                problems.append(CalcProblem(IssueType.INPUT_BLOCKED, item, "未確定の入力"))
                failed = True
                continue
            maximum = rule.max_scores[item]
            kind = v.value.kind
            if kind in _NUMERIC:
                number = Fraction(v.value.number)
                if not 0 <= number <= maximum:
                    problems.append(CalcProblem(IssueType.OUT_OF_RANGE, item, f"{v.value.number} が 0〜{maximum} の範囲外"))
                    failed = True
                    continue
                earned += number
                possible += maximum
                continue
            policy = rule.value_policies.get(kind)
            if policy is None:
                problems.append(CalcProblem(IssueType.BLANK_MEANING_UNKNOWN, item,
                                            f"{kind}（原文: {v.value.original!r}）の扱いが未定"))
                failed = True
            elif policy == Policy.SCORE_ZERO:
                possible += maximum
            # Policy.EXCLUDE: 分子・分母の両方から除く
        if failed:
            continue
        if possible == 0:
            problems.append(CalcProblem(IssueType.INCOMPLETE, None, f"{c.name} の対象項目がすべて除外された"))
            continue
        components.append(ComponentScore(c.name, c.weight * earned / possible, c.weight, tuple(evidence)))

    if problems:
        return problems

    unrounded = sum((c.score for c in components), Fraction(0))
    total = rule.rounding.apply(unrounded)
    if not 0 <= total <= 100:
        return [CalcProblem(IssueType.OUT_OF_RANGE, None, f"合計 {total} が 0〜100 の範囲外")]
    status = DataStatus.WARNING if any(v.status == DataStatus.WARNING for v in values) else DataStatus.CONFIRMED
    return SubjectResult(student_key, rule.subject, tuple(components), unrounded, total,
                         rule.grade_for(total), rule.rule_ref, status)
