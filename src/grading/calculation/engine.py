from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal

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
    score: Decimal
    weight: Decimal
    evidence_ids: tuple[int | str, ...]


@dataclass(frozen=True)
class SubjectResult:
    student_key: str
    subject: str
    components: tuple[ComponentScore, ...]
    unrounded_total: Decimal
    total: Decimal
    grade: str
    rule_ref: str
    status: DataStatus


def calculate(student_key: str, rule: SubjectRule, values: Mapping[str, ItemValue]) -> SubjectResult | list[CalcProblem]:
    problems: list[CalcProblem] = []
    known = {item for c in rule.components for item in c.items}
    for item in values:
        if item not in known:
            problems.append(CalcProblem(IssueType.ITEM_UNKNOWN, item, "採点ルールに無い項目"))

    components = []
    for c in rule.components:
        earned, possible, evidence = Decimal(0), Decimal(0), []
        for item in c.items:
            v = values.get(item)
            if v is None:
                problems.append(CalcProblem(IssueType.INCOMPLETE, item, "値が無い"))
                continue
            evidence.append(v.evidence_id)
            if v.status == DataStatus.BLOCKED:
                problems.append(CalcProblem(IssueType.INPUT_BLOCKED, item, "未確定の入力"))
                continue
            maximum = rule.max_scores[item]
            kind = v.value.kind
            if kind in _NUMERIC:
                if not 0 <= v.value.number <= maximum:
                    problems.append(CalcProblem(IssueType.OUT_OF_RANGE, item, f"{v.value.number} が 0〜{maximum} の範囲外"))
                    continue
                earned += v.value.number
                possible += maximum
                continue
            policy = rule.value_policies.get(kind)
            if policy is None:
                problems.append(CalcProblem(IssueType.BLANK_MEANING_UNKNOWN, item, f"{kind}（原文: {v.value.original!r}）の扱いが未定"))
            elif policy == Policy.SCORE_ZERO:
                possible += maximum
            # Policy.EXCLUDE: 分子・分母の両方から除く
        if possible == 0 and not any(p.item in c.items for p in problems):
            problems.append(CalcProblem(IssueType.INCOMPLETE, None, f"{c.name} の対象項目がすべて除外された"))
            continue
        if possible:
            components.append(ComponentScore(c.name, c.weight * earned / possible, c.weight, tuple(evidence)))

    if problems:
        return problems

    unrounded = sum((c.score for c in components), Decimal(0))
    total = rule.rounding.apply(unrounded)
    if not 0 <= total <= 100:
        return [CalcProblem(IssueType.OUT_OF_RANGE, None, f"合計 {total} が 0〜100 の範囲外")]
    status = DataStatus.WARNING if any(v.status == DataStatus.WARNING for v in values.values()) else DataStatus.CONFIRMED
    return SubjectResult(student_key, rule.subject, tuple(components), unrounded, total,
                         rule.grade_for(total), rule.rule_ref, status)
