from decimal import Decimal

from grading.calculation import ItemValue, SubjectResult, calculate
from grading.domain.enums import DataStatus, IssueType
from grading.normalization import parse_value
from grading.rules import SubjectRule
from tests.test_rules import AI_KISO, _with

RULE = SubjectRule.from_dict(AI_KISO)


def _values(rule=RULE, status=DataStatus.CONFIRMED, **raw):
    base = {"出席": 15, "課題1": 8, "課題2": 9, "期末試験": 90}
    base.update(raw)
    return {k: ItemValue(k, parse_value(v, rule.markers), f"E-{k}", status) for k, v in base.items()}


def _problem_types(result):
    assert isinstance(result, list), result
    return {p.issue_type for p in result}


def test_weighted_total_and_grade():
    r = calculate("S00123", RULE, _values())
    assert isinstance(r, SubjectResult)
    # 出席 15/15*20=20, 課題 17/20*40=34, 試験 90/100*40=36 → 90 → A
    assert [c.score for c in r.components] == [Decimal(20), Decimal(34), Decimal(36)]
    assert (r.total, r.grade, r.status) == (Decimal(90), "A", DataStatus.CONFIRMED)


def test_every_component_carries_its_evidence():
    r = calculate("S00123", RULE, _values())
    assert r.components[1].evidence_ids == ("E-課題1", "E-課題2")


def test_rounding_follows_the_rule_and_happens_before_grading():
    # 試験 89 → 35.6, 合計 89.6 → 四捨五入 90 → A
    r = calculate("S00123", RULE, _values(期末試験=89))
    assert (r.unrounded_total, r.total, r.grade) == (Decimal("89.6"), Decimal(90), "A")
    down = SubjectRule.from_dict(_with(rounding="DOWN_INT"))
    assert calculate("S00123", down, _values(rule=down, 期末試験=89)).grade == "B"


def test_blank_is_never_scored_as_zero():
    assert _problem_types(calculate("S00123", RULE, _values(課題1=None))) == {IssueType.BLANK_MEANING_UNKNOWN}


def test_absent_without_a_policy_blocks():
    assert _problem_types(calculate("S00123", RULE, _values(期末試験="欠"))) == {IssueType.BLANK_MEANING_UNKNOWN}


def test_not_submitted_follows_the_rules_policy():
    r = calculate("S00123", RULE, _values(課題1="未提出"))
    assert r.components[1].score == Decimal(18)   # 9/20*40


def test_excluded_item_is_removed_from_numerator_and_denominator():
    rule = SubjectRule.from_dict(_with(value_policies={"NOT_APPLICABLE": "EXCLUDE"}, markers={"対象外": "NOT_APPLICABLE"}))
    r = calculate("S00123", rule, _values(rule=rule, 課題1="対象外"))
    assert r.components[1].score == Decimal(36)   # 9/10*40


def test_zero_is_scored_as_zero():
    r = calculate("S00123", RULE, _values(課題1=0))
    assert r.components[1].score == Decimal(18)


def test_out_of_range_values_block():
    assert _problem_types(calculate("S00123", RULE, _values(期末試験=105))) == {IssueType.OUT_OF_RANGE}
    assert _problem_types(calculate("S00123", RULE, _values(出席=16))) == {IssueType.OUT_OF_RANGE}
    assert _problem_types(calculate("S00123", RULE, _values(課題2=-1))) == {IssueType.OUT_OF_RANGE}


def test_missing_item_blocks():
    values = _values()
    del values["期末試験"]
    assert _problem_types(calculate("S00123", RULE, values)) == {IssueType.INCOMPLETE}


def test_item_not_in_the_rule_blocks():
    values = _values()
    values["課題9"] = ItemValue("課題9", parse_value(10, {}), "E-x", DataStatus.CONFIRMED)
    assert _problem_types(calculate("S00123", RULE, values)) == {IssueType.ITEM_UNKNOWN}


def test_blocked_input_is_never_calculated():
    values = _values()
    values["課題1"] = ItemValue("課題1", parse_value(8, {}), "E-1", DataStatus.BLOCKED)
    assert _problem_types(calculate("S00123", RULE, values)) == {IssueType.INPUT_BLOCKED}


def test_warning_input_makes_the_result_a_warning():
    assert calculate("S00123", RULE, _values(status=DataStatus.WARNING)).status == DataStatus.WARNING


def test_all_problems_are_reported_at_once():
    types = _problem_types(calculate("S00123", RULE, _values(課題1=None, 期末試験=105)))
    assert types == {IssueType.BLANK_MEANING_UNKNOWN, IssueType.OUT_OF_RANGE}
