from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from grading.calculation import ItemValue, SubjectResult
from grading.rules import RuleBook
from grading.validation import Matrix, recheck


@dataclass(frozen=True)
class FinalizationReport:
    can_finalize: bool
    reasons: list[str]


def check_finalizable(
    *,
    open_blockers: int,
    matrix: Matrix,
    results: Mapping[tuple[str, str], tuple[SubjectResult, Sequence[ItemValue]]],
    rules: RuleBook,
    evidence_owner: Callable[[int | str], str | None],
) -> FinalizationReport:
    """出力しようとしている結果そのものを、ここで検算してから完成可否を決める。"""
    reasons = []
    if open_blockers:
        reasons.append(f"未回答の確認事項が {open_blockers} 件ある")
    if not matrix.expected:
        reasons.append("履修の組み合わせが1件も無い")
    if matrix.gaps() or matrix.unexpected or matrix.off_axis:
        reasons.append(f"学生×科目に欠損・未確定が {len(matrix.gaps())} 件、想定外の結果が "
                       f"{len(matrix.unexpected)} 件、一覧に無い履修が {len(matrix.off_axis)} 件ある")

    missing = [p for p in matrix.expected if p not in results]
    if missing:
        reasons.append(f"出力する結果が無い組み合わせが {len(missing)} 件ある")
    mismatched, failed = 0, 0
    for pair, (result, values) in results.items():
        if (result.student_key, result.subject) != pair or matrix.results.get(pair) != result.status:
            mismatched += 1
            continue
        try:
            rule = rules.get(result.subject)
        except KeyError:
            failed += 1
            continue
        if recheck(result, rule, values, evidence_owner):
            failed += 1
    if mismatched:
        reasons.append(f"表と出力する結果の状態が食い違うものが {mismatched} 件ある")
    if failed:
        reasons.append(f"検算の食い違いが {failed} 件ある")
    return FinalizationReport(not reasons, reasons)
