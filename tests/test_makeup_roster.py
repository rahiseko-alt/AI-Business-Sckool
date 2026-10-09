"""前期の追試の出席簿: 評定 E の科目だけ、例外処置は入れない、学科→学籍番号の順。"""

from fractions import Fraction

from grading.export.makeup_roster import build, targets
from grading.export.report_card import Card, Line


def _card(dept, sid, lines):
    return Card(dept, sid, f"NAME {sid}", f"カナ {sid}", tuple(lines), 100, Fraction(90))


def _line(name, grade, score=50, withheld=False):
    return Line(name=name, kind="講義", credits=2, score=score, grade=grade, withheld=withheld,
                withheld_grade="F" if withheld else "")


def test_only_e_and_not_exceptions_sorted_by_dept_then_id():
    cards = [_card("総合ビジネス科", "AIBC26003", [_line("A", "E")]),
             _card("国際ビジネス科", "AIBC26009", [_line("A", "E"), _line("B", "C", 75)]),
             _card("国際ビジネス科", "AIBC26001", [_line("A", "E", None, withheld=True), _line("B", "E", 40)])]
    t = targets(cards)
    assert list(t) == ["A", "B"]
    assert [c.student_id for c, _ in t["A"]] == ["AIBC26009", "AIBC26003"]
    assert [(c.student_id, s) for c, s in t["B"]] == [("AIBC26001", 40)]


def test_workbook_has_summary_and_one_sheet_per_subject():
    cards = [_card("国際ビジネス科", "AIBC26001", [_line("ビジネス日本語Ⅰ", "E", 48.04)])]
    wb = build(cards)
    assert wb.sheetnames == ["一覧", "ビジネス日本語Ⅰ"]
    ws = wb["ビジネス日本語Ⅰ"]
    assert [ws.cell(6, c).value for c in range(1, 7)] == [1, "国際ビジネス科", "AIBC26001", "NAME AIBC26001",
                                                          "カナ AIBC26001", 48.0]
    assert wb["一覧"]["B4"].value == 1
