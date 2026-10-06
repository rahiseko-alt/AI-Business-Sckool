import shutil
import subprocess

import pytest
from openpyxl import Workbook, load_workbook

from grading.term2.layout import (FIRST_ROW, LINKS_SHEET, SUBMISSION_TAB, SUBMITTED_CELL, gradebook_cells,
                                  submission_cells)


def _sub():
    return submission_cells("試作科目", "担当先生", ["TEST01", "TEST02"])


def test_submission_has_points_submitted_and_student_rows():
    cells = _sub()
    assert cells.values[0][:2] == ["科目名", "試作科目"] and cells.values[0][3] == "担当先生"
    assert cells.values[2][0] == "学籍番号" and cells.values[2][11] == "合計"
    assert [r[0] for r in cells.values[FIRST_ROW - 1:]] == ["TEST01", "TEST02"]


def test_yellow_is_only_points_submitted_and_manual_columns():
    cells = _sub()
    assert set(cells.yellow) == {"E2", "H2", "K2", SUBMITTED_CELL, "D4:D5", "G4:G5", "J4:J5"}
    assert all(cells.values[1][ord(c) - ord("A")] is None for c in "EHK")   # 配点の黄の欄は空で始まる


def test_red_rules_cover_points_total_and_every_adopted_column():
    rules = dict(_sub().red)
    assert "L2" in rules and "100" in rules["L2"]
    for col in "EHK":
        rng = f"{col}4:{col}5"
        assert rng in rules
        f = rules[rng]
        assert "ISNUMBER" in f and f"{col}$2" in f and SUBMITTED_CELL.replace("F", "$F$") in f


def test_gradebook_reads_adopted_values_and_submitted_through_links_only():
    cells = gradebook_cells(["試作科目"], rows=2)
    url_cell = f"{LINKS_SHEET}!$B${FIRST_ROW}"
    formulas = [f for row in cells.tabs["集計"] for f in row if isinstance(f, str) and f.startswith("=")]
    assert len(formulas) == 2 and all(url_cell in f for f in formulas)
    assert all("docs.google.com" not in f for f in formulas)       # ファイルを直接名指ししない
    assert any(f"'{SUBMISSION_TAB}'!{SUBMITTED_CELL}" in f for f in formulas)
    assert any("1,5,8,11,12" in f for f in formulas)                # 学籍番号・採用値3つ・合計
    assert cells.tabs[LINKS_SHEET][3][0] == "試作科目" and cells.yellow[LINKS_SHEET] == ["B4:B5"]   # 科目のアドレスと出席簿のアドレス


def _has_calc() -> bool:
    return shutil.which("soffice") is not None and subprocess.run(
        ["dpkg", "-s", "libreoffice-calc"], capture_output=True).returncode == 0


@pytest.mark.skipif(not _has_calc(), reason="LibreOffice Calc が無いため式の再計算を確認できない")
def test_manual_input_wins_over_auto_and_falls_back_when_cleared(tmp_path):
    cells = _sub()
    wb = Workbook()
    ws = wb.active
    for r, row in enumerate(cells.values, 1):
        for c, v in enumerate(row, 1):
            ws.cell(r, c, v)
    ws["C4"], ws["D4"] = 30, 25        # 自動30・手入力25 → 25
    ws["C5"], ws["D5"] = 30, None      # 手入力なし → 自動の30
    ws["G4"], ws["J4"] = 20, 40
    src = tmp_path / "s.xlsx"
    wb.save(src)
    out = tmp_path / "out"
    subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp_path}/profile", "--headless", "--convert-to",
                    "xlsx:Calc MS Excel 2007 XML", "--outdir", str(out), str(src)],
                   check=True, capture_output=True, timeout=180)
    got = load_workbook(out / "s.xlsx", data_only=True).active
    assert got["E4"].value == 25 and got["E5"].value == 30
    assert got["L4"].value == 85


# ---------- 出席の受け口と出席の自動計算（#12） ----------

from grading.term2.layout import ATTENDANCE_COPY, INTAKE_SHEET, LINK_SHEET_ATTENDANCE  # noqa: E402
from grading.validation.workbook_check import expected_points  # noqa: E402


def test_gradebook_has_intake_reading_attendance_book_only_through_links():
    book = gradebook_cells(["試作科目"], rows=2, student_ids=["TEST01", "TEST02"])
    assert book.tabs[LINKS_SHEET][FIRST_ROW][0] == "出席簿"          # 科目の次の行に出席簿のアドレス
    link = [f for row in book.tabs[LINK_SHEET_ATTENDANCE] for f in row if isinstance(f, str) and f.startswith("=")]
    assert link and all(f"{LINKS_SHEET}!$B${FIRST_ROW + 1}" in f for f in link)
    intake = book.tabs[INTAKE_SHEET]
    assert [r[:2] for r in intake[FIRST_ROW - 1:]] == [["TEST01", "試作科目"], ["TEST02", "試作科目"]]
    # 受け口の式は出席簿を直接読まず、つなぎのシートだけを見る
    formulas = [f for row in intake for f in row if isinstance(f, str) and f.startswith("=")]
    assert formulas and all("IMPORTRANGE" not in f for f in formulas)
    assert set(book.yellow[INTAKE_SHEET]) == {f"F{FIRST_ROW}:H{FIRST_ROW + 1}"}
    assert book.red[INTAKE_SHEET]


def test_submission_auto_attendance_reads_gradebook_copy_and_marks_bad_counts_red():
    cells = submission_cells("試作科目", "担当先生", ["TEST01"])
    assert "C4:C4" in dict(cells.red)
    assert ATTENDANCE_COPY in cells.extra_tabs
    assert "IMPORTRANGE" in cells.extra_tabs[ATTENDANCE_COPY][FIRST_ROW - 1][0]


CASES = [  # 授業数, 欠席, 遅刻
    (30, 0, 0), (30, 1, 0), (30, 0, 2), (30, 1, 1), (30, 2, 0), (30, 3, 1), (25, 1, 0), (25, 10, 0),
    (25, 9, 3), (30, 12, 0), (30, 11, 2), (45, 7, 5), (16, 3, 2), (30, 12, 1),
]
BAD = [(0, 0, 0), (None, 0, 0), (10, 11, 0)]


@pytest.mark.skipif(not _has_calc(), reason="LibreOffice Calc が無いため式の再計算を確認できない")
@pytest.mark.parametrize("maximum", [10, 20])
def test_auto_attendance_matches_first_term_rule(tmp_path, maximum):
    ids = [f"S{i:02d}" for i in range(len(CASES) + len(BAD))]
    cells = submission_cells("試作科目", "担当先生", ids)
    wb = Workbook()
    ws = wb.active
    ws.title = SUBMISSION_TAB
    for r, row in enumerate(cells.values, 1):
        for c, v in enumerate(row, 1):
            ws.cell(r, c, v)
    ws["E2"] = maximum
    copy = wb.create_sheet(ATTENDANCE_COPY)       # 成績表から写した受け口（IMPORTRANGE の代わりに値で置く）
    for k, (sid, (n, a, late)) in enumerate(zip(ids, CASES + BAD)):
        r = FIRST_ROW + k
        copy.cell(r, 1, sid), copy.cell(r, 2, "試作科目")
        copy.cell(r, 9, n), copy.cell(r, 10, a), copy.cell(r, 11, late)
    src = tmp_path / "a.xlsx"
    wb.save(src)
    out = tmp_path / "out"
    subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp_path}/profile", "--headless", "--convert-to",
                    "xlsx:Calc MS Excel 2007 XML", "--outdir", str(out), str(src)],
                   check=True, capture_output=True, timeout=180)
    got = load_workbook(out / "a.xlsx", data_only=True)[SUBMISSION_TAB]
    for k, (n, a, late) in enumerate(CASES):
        assert got.cell(FIRST_ROW + k, 3).value == expected_points(n, a, late, maximum, maximum // 10), (n, a, late)
    for k in range(len(BAD)):
        assert got.cell(FIRST_ROW + len(CASES) + k, 3).value == "要確認"
