from collections.abc import Callable
from decimal import Decimal
from fractions import Fraction

from grading.calculation import SubjectResult


def format_number(value: Fraction) -> str:
    """有限小数ならそのまま、割り切れなければ小数第2位までに「≒」を付けて表示する。"""
    d = value.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    if d == 1:
        return f"{(Decimal(value.numerator) / Decimal(value.denominator)).normalize():f}"
    return f"≒{float(value):.2f}"


def provenance(result: SubjectResult, locate: Callable[[int | str], str]) -> list[str]:
    """最終評価から元資料のセルまでを逆引きした行を返す。locate は根拠IDを「資料 / シート / セル」に変える。"""
    lines = [f"{result.student_key} {result.subject} {result.grade}"]
    for c in result.components:
        lines.append(f"{c.component} {format_number(c.score)}点")
        lines.extend(f"  ← {locate(e)}" for e in c.evidence_ids)
    lines.append(f"合計 {format_number(result.total)} → 評価 {result.grade}")
    return lines
