from collections.abc import Callable

from grading.calculation import SubjectResult


def provenance(result: SubjectResult, locate: Callable[[int | str], str]) -> list[str]:
    """最終評価から元資料のセルまでを逆引きした行を返す。locate は根拠IDを「資料 / シート / セル」に変える。"""
    lines = [f"{result.student_key} {result.subject} {result.grade}"]
    for c in result.components:
        lines.append(f"{c.component} {c.score.normalize():f}点")
        lines.extend(f"  ← {locate(e)}" for e in c.evidence_ids)
    lines.append(f"合計 {result.total.normalize():f} → 評価 {result.grade}")
    return lines
