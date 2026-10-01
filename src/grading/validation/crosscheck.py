from collections.abc import Callable
from decimal import Decimal

from grading.calculation import SubjectResult
from grading.rules import SubjectRule


def _grade(total: Decimal, thresholds) -> str | None:
    best = None
    for grade, minimum in thresholds:
        if total >= minimum and (best is None or minimum > best[1]):
            best = (grade, minimum)
    return best[0] if best else None


def recheck(result: SubjectResult, rule: SubjectRule, evidence_owner: Callable[[int | str], str | None]) -> list[str]:
    """結果1件を検算し、見つかった食い違いを返す（空なら問題なし）。"""
    problems = []
    if result.subject != rule.subject:
        problems.append(f"科目が採点ルールと違う: {result.subject} / {rule.subject}")

    expected = [(c.name, c.weight) for c in rule.components]
    actual = [(c.component, c.weight) for c in result.components]
    if expected != actual:
        problems.append(f"評価項目・配点がルールと違う: {actual}")
    for c in result.components:
        if not 0 <= c.score <= c.weight:
            problems.append(f"{c.component} の得点 {c.score} が 0〜{c.weight} の範囲外")
        if not c.evidence_ids:
            problems.append(f"{c.component} に根拠が無い")
        for e in c.evidence_ids:
            owner = evidence_owner(e)
            if owner != result.student_key:
                problems.append(f"{c.component} の根拠 {e} が別の学生（{owner}）のもの")

    summed = sum((c.score for c in result.components), Decimal(0))
    if summed != result.unrounded_total:
        problems.append(f"合計が内訳の和と違う: {result.unrounded_total} / {summed}")
    if rule.rounding.apply(summed) != result.total:
        problems.append(f"端数処理後の合計が違う: {result.total}")
    if not 0 <= result.total <= 100:
        problems.append(f"合計 {result.total} が 0〜100 の範囲外")
    if _grade(result.total, rule.grade_thresholds) != result.grade:
        problems.append(f"評価の変換が違う: {result.total} → {result.grade}")
    return problems
