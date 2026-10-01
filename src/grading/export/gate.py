from dataclasses import dataclass

from grading.validation import Matrix


@dataclass(frozen=True)
class FinalizationReport:
    can_finalize: bool
    reasons: list[str]


def check_finalizable(*, open_blockers: int, matrix: Matrix, recheck_problems: list[str]) -> FinalizationReport:
    reasons = []
    if open_blockers:
        reasons.append(f"未回答の確認事項が {open_blockers} 件ある")
    if not matrix.complete:
        reasons.append(f"学生×科目に欠損・未確定が {len(matrix.gaps())} 件、想定外の結果が {len(matrix.unexpected)} 件ある")
    if recheck_problems:
        reasons.append(f"検算の食い違いが {len(recheck_problems)} 件ある")
    return FinalizationReport(not reasons, reasons)
