from grading.term2.layout import LINKS_SHEET, SUBMISSION_TAB, gradebook_cells, submission_cells


def test_submission_has_yellow_input_column_and_header():
    cells = submission_cells("試作科目", ["TEST01", "TEST02"])
    assert cells.values[2] == ["学籍番号", "点数"]
    assert [r[0] for r in cells.values[3:]] == ["TEST01", "TEST02"]
    assert cells.yellow == ["B4:B5"]


def test_gradebook_reads_submission_only_through_the_links_sheet():
    cells = gradebook_cells(["試作科目"], rows=2)
    url_cell = f"{LINKS_SHEET}!$B$4"
    formulas = [f for row in cells.tabs["集計"] for f in row if isinstance(f, str) and f.startswith("=")]
    assert formulas and all(url_cell in f for f in formulas)
    assert all("docs.google.com" not in f for f in formulas)       # ファイルを直接名指ししない
    assert f"'{SUBMISSION_TAB}'!A4:B5" in formulas[0]
    assert cells.tabs[LINKS_SHEET][3][0] == "試作科目" and cells.yellow[LINKS_SHEET] == ["B4"]
