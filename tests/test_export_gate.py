from grading.calculation import calculate
from grading.domain.enums import DataStatus
from grading.export import check_finalizable, provenance
from grading.validation import completeness_matrix
from tests.test_calculation import RULE, _values

COMPLETE = completeness_matrix(["S1"], ["AI基礎"], {("S1", "AI基礎")}, {("S1", "AI基礎"): DataStatus.CONFIRMED})
GAP = completeness_matrix(["S1"], ["AI基礎"], {("S1", "AI基礎")}, {})


def test_clean_state_can_be_finalized():
    report = check_finalizable(open_blockers=0, matrix=COMPLETE, recheck_problems=[])
    assert report.can_finalize and report.reasons == []


def test_any_blocker_gap_or_recheck_problem_prevents_finalizing():
    assert not check_finalizable(open_blockers=1, matrix=COMPLETE, recheck_problems=[]).can_finalize
    assert not check_finalizable(open_blockers=0, matrix=GAP, recheck_problems=[]).can_finalize
    assert not check_finalizable(open_blockers=0, matrix=COMPLETE, recheck_problems=["合計不一致"]).can_finalize


def test_all_reasons_are_listed():
    report = check_finalizable(open_blockers=2, matrix=GAP, recheck_problems=["x"])
    assert len(report.reasons) == 3


def test_provenance_traces_grade_back_to_cells():
    r = calculate("S00123", RULE, _values())
    where = {f"E-{k}": f"{f}.xlsx / AI基礎 / {c}" for k, f, c in [
        ("出席", "attendance", "G24"), ("課題1", "assignment", "H31"), ("課題2", "assignment", "H32"),
        ("期末試験", "exam", "C14")]}
    lines = provenance(r, locate=where.__getitem__)
    text = "\n".join(lines)
    assert "出席 20" in text and "attendance.xlsx / AI基礎 / G24" in text
    assert "assignment.xlsx / AI基礎 / H31" in text and "H32" in text
    assert lines[-1] == "合計 90 → 評価 A"
