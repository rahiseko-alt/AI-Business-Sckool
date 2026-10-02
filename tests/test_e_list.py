from openpyxl import Workbook, load_workbook

from grading.export.e_list import add_e_list, grade_rows


def _sheet():
    wb = Workbook()
    ws = wb.active
    ws["B3"], ws["E3"], ws["I3"] = "学籍番号", "マーケティング", "総合ビジネス概論"
    for c, h in zip("EFGH", ["出席", "授業態度", "合計", "評定"]):
        ws[f"{c}4"] = h
    for c, h in zip("IJK", ["学習参加", "合計", "評定"]):
        ws[f"{c}4"] = h
    ws["B6"], ws["C6"], ws["E6"], ws["F6"], ws["G6"], ws["H6"], ws["J6"], ws["K6"] = "AIBC26001", "TARO", 5, 4, 9, "E", 0, "E"
    ws["B7"], ws["C7"], ws["E7"], ws["F7"], ws["G7"], ws["H7"], ws["J7"], ws["K7"] = "AIBC26002", "HANA", 50, 40, 90, "A", 0, "E"
    ws["I7"] = 3
    return ws


def test_e_rows_skip_subjects_the_student_does_not_take():
    rows = grade_rows(_sheet())
    es = [(r.subject, r.student_id) for r in rows if r.grade == "E"]
    assert es == [("マーケティング", "AIBC26001"), ("総合ビジネス概論", "AIBC26002")]


def test_e_list_sheet_is_grouped_by_subject(tmp_path):
    wb = Workbook()
    add_e_list(wb, grade_rows(_sheet()))
    wb.save(tmp_path / "e.xlsx")
    ws = load_workbook(tmp_path / "e.xlsx")["E一覧"]
    assert [c.value for c in ws[1]] == ["科目", "学籍番号", "氏名", "合計", "評定"]
    assert list(ws.iter_rows(min_row=2, values_only=True)) == [
        ("マーケティング", "AIBC26001", "TARO", 9, "E"), ("総合ビジネス概論", "AIBC26002", "HANA", 0, "E")]


def test_personal_grade_table_has_one_row_per_student(tmp_path):
    from grading.export.e_list import add_personal_grades
    ws = _sheet()
    ws["L3"], ws["L6"], ws["L7"] = "GPA", 1.0, 3.5
    wb = Workbook()
    add_personal_grades(wb, grade_rows(ws), gpa_of(ws))
    wb.save(tmp_path / "p.xlsx")
    out = load_workbook(tmp_path / "p.xlsx")["個人別評定"]
    assert [c.value for c in out[1]] == ["学籍番号", "氏名", "マーケティング", "総合ビジネス概論", "GPA", "GPA評定"]
    assert [c.value for c in out[2]] == ["AIBC26001", "TARO", "E", "—", 1.0, None]
    assert [c.value for c in out[3]] == ["AIBC26002", "HANA", "A", "E", 3.5, None]


from grading.export.e_list import gpa_of  # noqa: E402
