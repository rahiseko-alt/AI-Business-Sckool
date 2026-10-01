from collections.abc import Mapping
from dataclasses import dataclass

from grading.validation import Matrix


@dataclass(frozen=True)
class FinalizationReport:
    can_finalize: bool
    reasons: list[str]


def check_finalizable(
    *, open_blockers: int, matrix: Matrix, rechecks: Mapping[tuple[str, str], list[str]]
) -> FinalizationReport:
    """rechecks は (学生, 科目) ごとの検算結果。検算していない組み合わせがあれば完成扱いにしない。"""
    reasons = []
    if open_blockers:
        reasons.append(f"未回答の確認事項が {open_blockers} 件ある")
    if not matrix.expected:
        reasons.append("履修の組み合わせが1件も無い")
    if matrix.gaps() or matrix.unexpected or matrix.off_axis:
        reasons.append(f"学生×科目に欠損・未確定が {len(matrix.gaps())} 件、想定外の結果が "
                       f"{len(matrix.unexpected)} 件、一覧に無い履修が {len(matrix.off_axis)} 件ある")
    unchecked = [p for p in matrix.expected if p not in rechecks]
    if unchecked:
        reasons.append(f"検算していない組み合わせが {len(unchecked)} 件ある")
    failed = sum(1 for problems in rechecks.values() if problems)
    if failed:
        reasons.append(f"検算の食い違いが {failed} 件ある")
    return FinalizationReport(not reasons, reasons)
