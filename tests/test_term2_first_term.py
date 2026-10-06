from fractions import Fraction

import pytest

from grading.export.report_card import Card, Line
from grading.term2.first_term import apply_exceptions, sheet_rows


def _card(sid="S01"):
    return Card("国際", sid, "NAME", "ナマエ",
                (Line("科目A", "講義", 3, 70, "C"), Line("科目B", "講義", 2, 40, "E"), Line("科目C", "講義", 2, 88.5, "B")),
                hours=60, attended=Fraction(170, 3))


def test_rows_carry_score_grade_credits_and_totals():
    lines, totals = sheet_rows([_card()])
    assert lines[0] == ["S01", "NAME", "国際", "科目A", "講義", 70, "C", 3, 3]
    assert lines[1][-1] is None                                  # E は取得なし
    assert totals == [["S01", 7, 5, 60, pytest.approx(170 / 3)]]


def test_exception_blanks_score_and_earned_and_shows_given_grade():
    cards = apply_exceptions([_card()], {("S01", "科目A"): "F"})
    lines, totals = sheet_rows(cards)
    assert lines[0][5:] == [None, "F", 3, None]
    assert totals[0][1:3] == [7, 2]                              # 設定は変わらず、取得から外れる


def test_unknown_exception_target_stops():
    with pytest.raises(ValueError):
        apply_exceptions([_card()], {("S01", "無い科目"): "F"})
