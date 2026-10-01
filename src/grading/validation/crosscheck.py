"""計算結果の検算。計算エンジンのコードは使わず、元の値から別の手順で計算し直して突き合わせる。"""

from collections.abc import Callable, Iterable, Mapping
from fractions import Fraction

from grading.calculation import ItemValue, SubjectResult
from grading.calculation.engine import as_list
from grading.domain.enums import DataStatus, ValueKind
from grading.rules import Policy, SubjectRule


def _expected_component(rule: SubjectRule, items: tuple[str, ...], values: dict[str, ItemValue]) -> Fraction | str:
    numerator, denominator = Fraction(0), Fraction(0)
    for item in items:
        v = values.get(item)
        if v is None or v.status == DataStatus.BLOCKED:
            return f"{item} の値が無いか未確定"
        cap = rule.max_scores[item]
        if v.value.number is not None and v.value.kind in (ValueKind.NUMBER, ValueKind.ZERO):
            x = Fraction(v.value.number)
            if x < 0 or x > cap:
                return f"{item} の値 {x} が範囲外"
            numerator, denominator = numerator + x, denominator + cap
        elif rule.value_policies.get(v.value.kind) == Policy.SCORE_ZERO:
            denominator += cap
        elif rule.value_policies.get(v.value.kind) != Policy.EXCLUDE:
            return f"{item} の値 {v.value.kind} の扱いが未定"
    if denominator == 0:
        return "対象項目がすべて除外されている"
    return numerator / denominator


def _grade(total: Fraction, thresholds) -> str | None:
    best = None
    for grade, minimum in thresholds:
        if total >= minimum and (best is None or minimum > best[1]):
            best = (grade, minimum)
    return best[0] if best else None


def recheck(
    result: SubjectResult,
    rule: SubjectRule,
    values: Mapping[str, ItemValue] | Iterable[ItemValue],
    evidence_owner: Callable[[int | str], str | None],
) -> list[str]:
    """結果1件を検算し、見つかった食い違いを返す（空なら問題なし）。"""
    problems = []
    values = as_list(values)
    by_item: dict[str, ItemValue] = {}
    for v in values:
        if v.item in by_item:
            problems.append(f"{v.item} の値が複数ある")
        by_item[v.item] = v
    rule_items = {i for c in rule.components for i in c.items}
    for extra in sorted(set(by_item) - rule_items):
        problems.append(f"ルールに無い項目 {extra} の値がある")

    if result.subject != rule.subject:
        problems.append(f"科目が採点ルールと違う: {result.subject} / {rule.subject}")
    if result.rule_ref != rule.rule_ref:
        problems.append(f"採点ルールの根拠が違う: {result.rule_ref} / {rule.rule_ref}")
    if [(c.name, c.weight) for c in rule.components] != [(c.component, c.weight) for c in result.components]:
        problems.append("評価項目・配点がルールと違う")

    recomputed = Fraction(0)
    for rc, c in zip(rule.components, result.components):
        ratio = _expected_component(rule, rc.items, by_item)
        if isinstance(ratio, str):
            problems.append(f"{rc.name}: {ratio}")
            continue
        expected = rc.weight * ratio
        recomputed += expected
        if c.score != expected:
            problems.append(f"{rc.name} の得点が検算と違う: {c.score} / {expected}")
        expected_evidence = {by_item[i].evidence_id for i in rc.items}
        if set(c.evidence_ids) != expected_evidence:
            problems.append(f"{rc.name} の根拠が項目の値と一致しない")
        for e in c.evidence_ids:
            owner = evidence_owner(e)
            if owner != result.student_key:
                problems.append(f"{rc.name} の根拠 {e} が別の学生（{owner}）のもの")

    if recomputed != result.unrounded_total:
        problems.append(f"合計が検算と違う: {result.unrounded_total} / {recomputed}")
    if recomputed < 0 or result.total != rule.rounding.apply(recomputed):
        problems.append(f"端数処理後の合計が違う: {result.total}")
    if not 0 <= result.total <= 100:
        problems.append(f"合計 {result.total} が 0〜100 の範囲外")
    if _grade(result.total, rule.grade_thresholds) != result.grade:
        problems.append(f"評価の変換が違う: {result.total} → {result.grade}")
    return problems
