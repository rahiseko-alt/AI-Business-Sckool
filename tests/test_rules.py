from decimal import Decimal

import pytest

from grading.domain.enums import ValueKind
from grading.rules import Policy, RuleBook, RuleError, SubjectRule

AI_KISO = {
    "subject": "AI基礎",
    "rule_ref": "SRC:採点基準.xlsx",
    "components": [
        {"name": "出席", "weight": 20, "items": ["出席"]},
        {"name": "課題", "weight": 40, "items": ["課題1", "課題2"]},
        {"name": "試験", "weight": 40, "items": ["期末試験"]},
    ],
    "max_scores": {"出席": 15, "課題1": 10, "課題2": 10, "期末試験": 100},
    "grade_thresholds": [["A", 90], ["B", 80], ["C", 70], ["D", 60], ["E", 0]],
    "markers": {"未提出": "NOT_SUBMITTED", "欠": "ABSENT"},
    "value_policies": {"NOT_SUBMITTED": "SCORE_ZERO"},
}


def _with(**changes):
    return {**AI_KISO, **changes}


def test_complete_rule_is_accepted():
    rule = SubjectRule.from_dict(AI_KISO)
    assert rule.subject == "AI基礎"
    assert rule.max_scores["期末試験"] == Decimal("100")
    assert rule.markers["欠"] == ValueKind.ABSENT
    assert rule.value_policies[ValueKind.NOT_SUBMITTED] == Policy.SCORE_ZERO


@pytest.mark.parametrize(
    "broken, expected",
    [
        (_with(components=[{"name": "課題", "weight": 90, "items": ["課題1"]}]), "合計"),
        (_with(max_scores={"出席": 15, "課題1": 10, "期末試験": 100}), "課題2"),
        (_with(grade_thresholds=None), "ABCDE"),
        (_with(grade_thresholds=[["A", 90], ["B", 80]]), "0"),
        (_with(grade_thresholds=[["A", 90], ["B", 90], ["E", 0]]), "重複"),
        (_with(rule_ref=""), "根拠"),
        (_with(value_policies={"ABSENT": "AVERAGE"}), "AVERAGE"),
    ],
)
def test_incomplete_or_invented_rules_are_rejected_with_reasons(broken, expected):
    with pytest.raises(RuleError) as e:
        SubjectRule.from_dict(broken)
    assert any(expected in p for p in e.value.problems)


def test_rule_cannot_be_borrowed_from_another_subject():
    book = RuleBook([SubjectRule.from_dict(AI_KISO)])
    assert book.get("AI基礎").subject == "AI基礎"
    with pytest.raises(KeyError):
        book.get("AI応用")


def test_two_rules_for_one_subject_are_rejected():
    with pytest.raises(ValueError):
        RuleBook([SubjectRule.from_dict(AI_KISO), SubjectRule.from_dict(AI_KISO)])
