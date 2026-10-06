from dataclasses import replace

from grading.calculation import calculate
from grading.domain.enums import DataStatus
from grading.validation import Cell, completeness_matrix, recheck
from tests.test_calculation import RULE, _values


VALUES = _values()


def _result():
    return calculate("S00123", RULE, VALUES)


def test_a_correct_result_passes_the_recheck():
    assert recheck(_result(), RULE, VALUES, evidence_owner=lambda e: "S00123") == []


def test_tampered_total_is_detected():
    bad = replace(_result(), total=95)
    assert any("合計" in p for p in recheck(bad, RULE, VALUES, evidence_owner=lambda e: "S00123"))


def test_wrong_grade_is_detected():
    bad = replace(_result(), grade="B")
    assert any("評価" in p for p in recheck(bad, RULE, VALUES, evidence_owner=lambda e: "S00123"))


def test_result_from_another_subjects_rule_is_detected():
    bad = replace(_result(), subject="マーケティング")
    assert any("科目" in p for p in recheck(bad, RULE, VALUES, evidence_owner=lambda e: "S00123"))


def test_other_students_evidence_mixed_in_is_detected():
    owners = {"E-課題2": "S00456"}
    problems = recheck(_result(), RULE, VALUES, evidence_owner=lambda e: owners.get(e, "S00123"))
    assert any("別の学生" in p for p in problems)


def test_component_without_evidence_is_detected():
    r = _result()
    bad = replace(r, components=(replace(r.components[0], evidence_ids=()), *r.components[1:]))
    assert any("根拠" in p for p in recheck(bad, RULE, VALUES, evidence_owner=lambda e: "S00123"))


def test_matrix_marks_ok_missing_unresolved_and_not_enrolled():
    expected = {("S1", "AI基礎"), ("S1", "IT"), ("S2", "AI基礎"), ("S2", "IT")}
    results = {("S1", "AI基礎"): DataStatus.CONFIRMED, ("S1", "IT"): DataStatus.WARNING,
               ("S2", "AI基礎"): DataStatus.BLOCKED}
    m = completeness_matrix(["S1", "S2", "S3"], ["AI基礎", "IT"], expected, results)
    assert m.cells["S1"]["AI基礎"] == Cell.OK
    assert m.cells["S1"]["IT"] == Cell.OK_WARNING
    assert m.cells["S2"]["AI基礎"] == Cell.UNRESOLVED
    assert m.cells["S2"]["IT"] == Cell.MISSING
    assert m.cells["S3"]["IT"] == Cell.NOT_ENROLLED
    assert not m.complete
    assert ("S2", "IT") in m.gaps() and ("S2", "AI基礎") in m.gaps()


def test_result_for_unenrolled_or_unknown_pair_is_a_gap():
    m = completeness_matrix(["S1"], ["AI基礎"], set(), {("S1", "AI基礎"): DataStatus.CONFIRMED,
                                                       ("S9", "AI基礎"): DataStatus.CONFIRMED})
    assert not m.complete
    assert set(m.unexpected) == {("S1", "AI基礎"), ("S9", "AI基礎")}


def test_full_matrix_is_complete():
    m = completeness_matrix(["S1"], ["AI基礎"], {("S1", "AI基礎")}, {("S1", "AI基礎"): DataStatus.CONFIRMED})
    assert m.complete and m.gaps() == []


def test_only_confirmed_or_warning_counts_as_present():
    m = completeness_matrix(["S1"], ["X"], {("S1", "X")}, {("S1", "X"): "LIKELY"})
    assert not m.complete and ("S1", "X") in m.gaps()
