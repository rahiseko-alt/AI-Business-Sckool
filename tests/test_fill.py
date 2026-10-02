from fractions import Fraction

import pytest
from openpyxl import Workbook, load_workbook

from grading.export.fill import FilledValue, fill_template


def _blank(path):
    wb = Workbook()
    ws = wb.active
    ws["A1"] = "2026年度　国際ビジネス科（AI計算版）"
    ws["B3"] = "学籍番号"
    ws["E3"], ws["E4"], ws["F4"], ws["G4"] = "マーケティング", "出席", "授業態度", "筆記テスト"
    ws["H3"], ws["H4"], ws["I4"] = "AI演習（実践）", "出席", "授業態度"
    ws.merge_cells("E3:G3")
    ws["B6"], ws["B7"] = "AIBC26001", "AIBC26002"
    wb.save(path)
    return path


def _v(sid, subject, item, value, ev=("出席簿!F6",)):
    return FilledValue(sid, subject, item, Fraction(value), "10 − 2 × 遅刻1回 = 8", tuple(ev))


def test_values_go_to_the_cell_found_by_subject_and_item(tmp_path):
    out = fill_template(_blank(tmp_path / "b.xlsx"), tmp_path / "o.xlsx",
                        [_v("AIBC26001", "マーケティング", "授業態度", 8), _v("AIBC26002", "AI演習", "授業態度", 10, ())])
    ws = load_workbook(out).worksheets[0]
    assert ws["F6"].value == 8 and ws["I7"].value == 10
    assert ws["E6"].value is None


def test_every_value_is_listed_with_its_formula_and_source(tmp_path):
    out = fill_template(_blank(tmp_path / "b.xlsx"), tmp_path / "o.xlsx", [_v("AIBC26001", "マーケティング", "授業態度", 8)])
    rows = list(load_workbook(out)["根拠"].iter_rows(min_row=2, values_only=True))
    assert rows == [("AIBC26001", "マーケティング", "授業態度", "F6", 8, "8", "10 − 2 × 遅刻1回 = 8", "出席簿!F6")]


def test_fractions_are_kept_exactly_in_the_evidence_sheet(tmp_path):
    out = fill_template(_blank(tmp_path / "b.xlsx"), tmp_path / "o.xlsx", [_v("AIBC26001", "マーケティング", "筆記テスト", Fraction(1, 3))])
    row = next(load_workbook(out)["根拠"].iter_rows(min_row=2, values_only=True))
    assert row[5] == "1/3"


@pytest.mark.parametrize("sid, subject, item", [("AIBC26999", "マーケティング", "授業態度"),
                                                ("AIBC26001", "経営学", "授業態度"),
                                                ("AIBC26001", "マーケティング", "発表")])
def test_unknown_student_subject_or_item_stops_instead_of_guessing(tmp_path, sid, subject, item):
    with pytest.raises(KeyError):
        fill_template(_blank(tmp_path / "b.xlsx"), tmp_path / "o.xlsx", [_v(sid, subject, item, 8)])


def test_writing_the_same_cell_twice_is_refused(tmp_path):
    with pytest.raises(ValueError):
        fill_template(_blank(tmp_path / "b.xlsx"), tmp_path / "o.xlsx",
                      [_v("AIBC26001", "マーケティング", "授業態度", 8), _v("AIBC26001", "マーケティング", "授業態度", 6)])


def _original(path):
    wb = Workbook()
    ws = wb.active
    ws.title = "２０２６年前期"
    ws["A1"] = "2026年度　国際ビジネス科"
    ws["B3"] = "学籍番号"
    ws["E3"], ws["E4"], ws["F4"], ws["G4"], ws["H4"] = "マーケティング", "出席", "授業態度", "筆記テスト", "合計"
    ws["I3"], ws["I4"], ws["J4"] = "ビジネス日本語", "出席", "授業態度"
    ws["B6"] = "AIBC26001"
    ws["E6"], ws["F6"], ws["G6"], ws["H6"] = "=10-((1-0.9)/0.04)", 8, 56, "=SUM(E6:G6)"
    ws["I6"], ws["J6"] = 7, 18
    wb.save(path)
    return path


def test_ai_workbook_overrides_only_ai_cells_and_keeps_the_original(tmp_path):
    from grading.export.fill import build_ai_workbook
    values = [_v("AIBC26001", "マーケティング", "出席", 9), _v("AIBC26001", "マーケティング", "授業態度", 10),
              _v("AIBC26001", "ビジネス日本語", "出席", 10)]
    teachers = {"マーケティング": "百井", "ビジネス日本語": "樋口"}
    out = build_ai_workbook(_original(tmp_path / "o.xlsx"), tmp_path / "ai.xlsx", values, teachers)
    wb = load_workbook(out)
    assert wb.sheetnames == ["AI計算版", "原本", "計算根拠_百井", "計算根拠_樋口"]
    ai, orig = wb["AI計算版"], wb["原本"]
    assert (ai["E6"].value, ai["F6"].value, ai["I6"].value) == (9, 10, 10)
    assert (ai["G6"].value, ai["H6"].value, ai["J6"].value) == (56, "=SUM(E6:G6)", 18)   # AI以外は原本のまま
    assert (orig["E6"].value, orig["F6"].value, orig["I6"].value) == ("=10-((1-0.9)/0.04)", 8, 7)
    assert ai["A1"].value.endswith("（AI計算版）") and orig["A1"].value == "2026年度　国際ビジネス科"
    assert ai["E6"].fill.fgColor.rgb.endswith("DDEBF7") and not orig["E6"].fill.fgColor.rgb.endswith("DDEBF7")
    rows = list(wb["計算根拠_百井"].iter_rows(min_row=2, values_only=True))
    assert [(r[1], r[2], r[3], r[4], r[5]) for r in rows] == [("マーケティング", "出席", "E6", "=10-((1-0.9)/0.04)", 9),
                                                             ("マーケティング", "授業態度", "F6", 8, 10)]


def test_ai_workbook_refuses_a_subject_without_a_teacher(tmp_path):
    from grading.export.fill import build_ai_workbook
    with pytest.raises(KeyError):
        build_ai_workbook(_original(tmp_path / "o.xlsx"), tmp_path / "ai.xlsx",
                          [_v("AIBC26001", "マーケティング", "出席", 9)], {})
