"""独立レビューで見つかった、誤った成績を確定し得る経路の再発防止。"""

from dataclasses import replace
from fractions import Fraction

import pytest

from grading.calculation import ItemValue, calculate
from grading.domain.enums import DataStatus, IssueType, MatchStatus
from grading.export import check_finalizable
from grading.identity import IdentityClaim, Student, resolve
from grading.normalization import NameDiff, compare_names, parse_value
from grading.rules import RuleError, SubjectRule
from grading.validation import completeness_matrix, recheck
from tests.test_calculation import RULE, _values
from tests.test_rules import AI_KISO, _with

THIRDS = {
    "subject": "X", "rule_ref": "s",
    "components": [{"name": "a", "weight": 20, "items": ["a"]}, {"name": "b", "weight": 20, "items": ["b"]},
                   {"name": "c", "weight": 60, "items": ["c"]}],
    "max_scores": {"a": 3, "b": 3, "c": 9},
    "grade_thresholds": [["C", 60], ["D", 0]],
}


def _iv(item, raw, evidence=None, status=DataStatus.CONFIRMED, markers=None):
    return ItemValue(item, parse_value(raw, markers or {}), evidence or f"E-{item}", status)


@pytest.mark.parametrize("rounding", ["NONE", "DOWN_INT", "HALF_UP_INT"])
def test_exact_arithmetic_keeps_a_true_60_at_60(rounding):
    rule = SubjectRule.from_dict({**THIRDS, "rounding": rounding})
    r = calculate("S", rule, [_iv("a", 2), _iv("b", 2), _iv("c", 5)])
    assert r.unrounded_total == Fraction(60) and r.total == 60 and r.grade == "C"


def _ok_owner(e):
    return "S00123"


def test_recheck_recomputes_from_the_item_values():
    values = _values()
    r = calculate("S00123", RULE, values)
    c = r.components
    forged = replace(r, components=(replace(c[0], score=Fraction(10)), *c[1:]),
                     unrounded_total=r.unrounded_total - 10, total=r.total - 10, grade="B")
    assert any("出席" in p for p in recheck(forged, RULE, values, _ok_owner))
    assert recheck(r, RULE, values, _ok_owner) == []


def test_recheck_detects_a_different_rule_reference():
    values = _values()
    r = replace(calculate("S00123", RULE, values), rule_ref="other")
    assert any("根拠" in p for p in recheck(r, RULE, values, _ok_owner))


def test_expected_pair_outside_the_axes_is_still_a_gap():
    m = completeness_matrix(["S1"], ["X"], {("S1", "X"), ("S2", "X")}, {("S1", "X"): DataStatus.CONFIRMED})
    assert not m.complete and ("S2", "X") in m.gaps()


def test_empty_expectation_is_never_complete():
    assert not completeness_matrix([], [], set(), {}).complete


@pytest.mark.parametrize("target", ["ZERO", "NUMBER", "BLANK", "UNKNOWN"])
def test_markers_may_only_mean_non_numeric_states(target):
    with pytest.raises(RuleError):
        SubjectRule.from_dict(_with(markers={"-": target}))


def test_blank_can_never_be_given_a_score_policy_by_rule():
    with pytest.raises(RuleError):
        SubjectRule.from_dict(_with(value_policies={"BLANK": "SCORE_ZERO"}))


def test_markers_colliding_after_normalization_are_rejected():
    with pytest.raises(RuleError):
        SubjectRule.from_dict(_with(markers={"欠": "ABSENT", "欠 ": "NOT_SUBMITTED"}))


def test_two_values_for_one_item_block_instead_of_last_one_winning():
    values = list(_values().values()) + [_iv("期末試験", 75, evidence="E-other")]
    problems = calculate("S00123", RULE, values)
    assert isinstance(problems, list) and {p.issue_type for p in problems} == {IssueType.DATA_CONFLICT}


def test_gate_requires_a_recheck_for_every_expected_pair():
    m = completeness_matrix(["S1"], ["X"], {("S1", "X")}, {("S1", "X"): DataStatus.CONFIRMED})
    assert not check_finalizable(open_blockers=0, matrix=m, rechecks={}).can_finalize
    assert check_finalizable(open_blockers=0, matrix=m, rechecks={("S1", "X"): []}).can_finalize
    assert not check_finalizable(open_blockers=0, matrix=m, rechecks={("S1", "X"): ["x"]}).can_finalize


def test_threshold_entries_must_be_pairs_not_strings():
    with pytest.raises(RuleError):
        SubjectRule.from_dict(_with(grade_thresholds=["A9", ["E", 0]]))


def test_compatibility_ideographs_are_different_names():
    assert compare_names("神田", "神田") == NameDiff.DIFFERENT


def test_student_number_case_is_significant():
    master = [Student("S1", "A001", "田中 太郎")]
    assert resolve(IdentityClaim(student_number="a001"), master).status == MatchStatus.UNMATCHED


def test_max_score_for_an_unknown_item_is_rejected_as_a_likely_typo():
    with pytest.raises(RuleError):
        SubjectRule.from_dict(_with(max_scores={**AI_KISO["max_scores"], "課題３": 10}))
