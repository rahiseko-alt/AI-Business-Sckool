from dataclasses import replace
from fractions import Fraction

from grading.calculation import calculate
from grading.domain.enums import DataStatus
from grading.export import check_finalizable, provenance
from grading.export.provenance import format_number
from grading.rules import RuleBook
from grading.validation import completeness_matrix
from tests.test_calculation import RULE, _values

PAIR = ("S00123", "AI基礎")
VALUES = _values()
RESULT = calculate("S00123", RULE, VALUES)
BOOK = RuleBook([RULE])
COMPLETE = completeness_matrix(["S00123"], ["AI基礎"], {PAIR}, {PAIR: DataStatus.CONFIRMED})
GAP = completeness_matrix(["S00123"], ["AI基礎"], {PAIR}, {})


def _owner(e):
    return "S00123"


def _check(*, open_blockers=0, matrix=COMPLETE, results=None):
    results = {PAIR: (RESULT, VALUES)} if results is None else results
    return check_finalizable(open_blockers=open_blockers, matrix=matrix, results=results, rules=BOOK,
                             evidence_owner=_owner)


def test_clean_state_can_be_finalized():
    report = _check()
    assert report.can_finalize and report.reasons == []


def test_any_blocker_or_gap_prevents_finalizing():
    assert not _check(open_blockers=1).can_finalize
    assert not _check(matrix=GAP).can_finalize


def test_gate_runs_the_recheck_itself_on_the_exported_result():
    forged = replace(RESULT, grade="B")
    report = _check(results={PAIR: (forged, VALUES)})
    assert not report.can_finalize and any("検算" in r for r in report.reasons)


def test_result_missing_for_a_present_cell_prevents_finalizing():
    assert not _check(results={}).can_finalize


def test_result_status_must_match_the_matrix():
    assert not _check(results={PAIR: (replace(RESULT, status=DataStatus.WARNING), VALUES)}).can_finalize


def test_all_reasons_are_listed():
    report = _check(open_blockers=2, matrix=GAP, results={PAIR: (replace(RESULT, grade="B"), VALUES)})
    assert len(report.reasons) >= 3


def test_provenance_traces_grade_back_to_cells():
    where = {f"E-{k}": f"{f}.xlsx / AI基礎 / {c}" for k, f, c in [
        ("出席", "attendance", "G24"), ("課題1", "assignment", "H31"), ("課題2", "assignment", "H32"),
        ("期末試験", "exam", "C14")]}
    lines = provenance(RESULT, locate=where.__getitem__)
    text = "\n".join(lines)
    assert "出席 20" in text and "attendance.xlsx / AI基礎 / G24" in text
    assert "assignment.xlsx / AI基礎 / H31" in text and "H32" in text
    assert lines[-1] == "合計 90 → 評価 A"


def test_numbers_are_shown_exactly_without_rounding():
    assert format_number(Fraction(448, 5)) == "89.6"
    assert format_number(Fraction(1, 8)) == "0.125"
    assert format_number(Fraction(200, 3)) == "200/3（66.666666…）"
    assert format_number(Fraction(239989, 3000)).startswith("239989/3000（79.996333…")
