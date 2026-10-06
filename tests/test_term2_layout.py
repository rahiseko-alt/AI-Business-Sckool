import re
import shutil
import subprocess

import pytest
from openpyxl import Workbook, load_workbook

from grading.term2.layout import (ATTENDANCE_COPY, EXCLUDE_SHEET, FIRST_ROW, INTAKE_SHEET, LINK_SHEET_ATTENDANCE,
                                  LINKS_SHEET, ROSTER_COPY, ROSTER_SHEET, SUBJECT_SHEET, SUBMISSION_TAB,
                                  SUBMITTED_CELL, SUMMARY_SHEET, gradebook_cells, master_cells, submission_cells)
from grading.validation.workbook_check import expected_points

ROSTER = [("K01", "国際一", "コク イチ", "国際"), ("S01", "総合一", "ソウ イチ", "総合"),
          ("K02", "国際二", "コク ニ", "国際"), ("K03", "国際三", "コク サン", "国際")]


def _sub(slots=3):
    return submission_cells("試作科目", "担当先生", "国際", slots=slots)


def _has_calc() -> bool:
    return shutil.which("soffice") is not None and subprocess.run(
        ["dpkg", "-s", "libreoffice-calc"], capture_output=True).returncode == 0


needs_calc = pytest.mark.skipif(not _has_calc(), reason="LibreOffice Calc が無いため式の再計算を確認できない")


def _recalc(cells, tmp_path, roster=ROSTER, excluded=(), intake=(), edits=None):
    """提出用の表を1つのファイルに見立て、写し（本物では IMPORTRANGE）を値で置いて再計算する。"""
    wb = Workbook()
    ws = wb.active
    ws.title = SUBMISSION_TAB
    for r, row in enumerate(cells.values, 1):
        for c, v in enumerate(row, 1):
            ws.cell(r, c, v)
    copy = wb.create_sheet(ROSTER_COPY)
    for r, row in enumerate(cells.extra_tabs[ROSTER_COPY], 1):
        for c, v in enumerate(row, 1):
            if c in (5,) and v is not None:      # 学科内の順番の式だけ残し、IMPORTRANGE は値で置き換える
                copy.cell(r, c, v)
    for k, row in enumerate(roster):
        for c, v in enumerate(row, 1):
            copy.cell(FIRST_ROW + k, c, v)
    for k, (sid, subject) in enumerate(excluded):
        copy.cell(FIRST_ROW + k, 7, sid), copy.cell(FIRST_ROW + k, 8, subject)
    att = wb.create_sheet(ATTENDANCE_COPY)
    for k, (sid, n, a, late) in enumerate(intake):
        r = FIRST_ROW + k
        att.cell(r, 1, sid), att.cell(r, 2, "試作科目")
        att.cell(r, 9, n), att.cell(r, 10, a), att.cell(r, 11, late)
    for addr, v in (edits or {}).items():
        ws[addr] = v
    src = tmp_path / "s.xlsx"
    wb.save(src)
    out = tmp_path / "out"
    subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp_path}/profile", "--headless", "--convert-to",
                    "xlsx:Calc MS Excel 2007 XML", "--outdir", str(out), str(src)],
                   check=True, capture_output=True, timeout=180)
    return load_workbook(out / "s.xlsx", data_only=True)[SUBMISSION_TAB]


# ---------- 提出用の表の形（#11） ----------

def test_submission_has_points_submitted_dept_and_headers():
    cells = _sub()
    assert cells.values[0][:2] == ["科目名", "試作科目"] and cells.values[0][3] == "担当先生"
    assert cells.values[0][6:8] == ["学科", "国際"]
    assert cells.values[2][0] == "学籍番号" and cells.values[2][11] == "合計"


def test_yellow_is_only_points_submitted_and_manual_columns():
    cells = _sub()
    assert set(cells.yellow) == {"E2", "H2", "K2", SUBMITTED_CELL, "D4:D6", "G4:G6", "J4:J6"}
    assert all(cells.values[1][ord(c) - ord("A")] is None for c in "EHK")   # 配点の黄の欄は空で始まる


def test_red_rules_cover_points_total_adopted_columns_and_unknown_ids():
    rules = dict(_sub().red)
    assert "L2" in rules and "100" in rules["L2"]
    for col in "EHK":
        f = rules[f"{col}4:{col}6"]
        assert "ISNUMBER" in f and f"{col}$2" in f and "$F$1" in f
    assert "COUNTIF" in rules["A4:A6"]                                  # 名簿に無い学籍番号


@needs_calc
def test_students_of_own_dept_listed_in_roster_order_and_manual_wins(tmp_path):
    got = _recalc(_sub(slots=4), tmp_path, edits={"C4": 30, "D4": 25, "C5": 30, "G4": 20, "J4": 40})
    assert [got.cell(r, 1).value for r in range(4, 8)] == ["K01", "K02", "K03", None]
    assert got["B4"].value == "国際一"
    assert got["E4"].value == 25 and got["E5"].value == 30             # 手入力が優先、無ければ自動
    assert got["L4"].value == 85


@needs_calc
def test_excluded_student_disappears_without_shifting_others(tmp_path):
    got = _recalc(_sub(), tmp_path, excluded=[("K02", "試作科目"), ("K03", "別の科目")])
    assert [got.cell(r, 1).value for r in range(4, 7)] == ["K01", None, "K03"]
    assert got["B5"].value is None


# ---------- 成績表（#10・#13） ----------

def test_master_sheets_are_yellow_and_hold_roster_and_subjects():
    book = master_cells(ROSTER, [("国際", "試作科目", "担当先生", 2, "講義")])
    assert book.tabs[ROSTER_SHEET][FIRST_ROW - 1] == ["K01", "国際一", "コク イチ", "国際"]
    assert book.tabs[SUBJECT_SHEET][FIRST_ROW - 1] == ["国際", "試作科目", "担当先生", 2, "講義"]
    assert book.yellow == {ROSTER_SHEET: ["A4:D7"], SUBJECT_SHEET: ["A4:E4"], EXCLUDE_SHEET: ["A4:B53"]}


def test_gradebook_lists_every_subject_and_reads_through_links_only():
    subjects = [("国際", "科目A"), ("総合", "科目A")]
    book = gradebook_cells(subjects, slots=3)
    assert [r[0] for r in book.tabs[LINKS_SHEET][FIRST_ROW - 1:]] == ["科目A", "科目A", "出席簿"]
    formulas = [f for row in book.tabs[SUMMARY_SHEET] for f in row if isinstance(f, str) and "IMPORTRANGE" in f]
    assert len(formulas) == 4                                              # 科目ごとに提出済みと点
    assert all("docs.google.com" not in f for f in formulas)
    assert all(f"INDEX({LINKS_SHEET}!$B$4:$B$5," in f for f in formulas)     # つなぎ先一覧の何番目かで読む
    blocks = book.tabs[SUMMARY_SHEET][FIRST_ROW - 1:]
    assert len(blocks) == 2 * 4                                            # 見出し＋学生3行 が科目ぶん
    shift = lambda row, k: tuple(re.sub(rf"(?<=[A-Z]){FIRST_ROW + k}\b", "#", str(v)) for v in row)
    assert {shift(blocks[k], k) + shift(blocks[k + 1], k + 1) for k in (0, 4)} == {shift(blocks[0], 0) + shift(blocks[1], 1)}
    assert any("1,5,8,11,12" in f for f in formulas)
    assert book.yellow[LINKS_SHEET] == ["B4:B6"]


def test_gradebook_has_intake_from_roster_and_subjects_reading_attendance_only_through_links():
    book = gradebook_cells([("国際", "科目A"), ("総合", "科目A")], slots=2)
    link = [f for row in book.tabs[LINK_SHEET_ATTENDANCE] for f in row if isinstance(f, str) and f.startswith("=")]
    assert link and all(f"{LINKS_SHEET}!$B${FIRST_ROW + 2}" in f for f in link)
    intake = book.tabs[INTAKE_SHEET][FIRST_ROW - 1:]
    assert len(intake) == 4                                                # 科目2つ × 2行
    # 行番号を除けば同じ式（1行書いて下へ写せる）
    same = {tuple(re.sub(rf"(?<=[A-Z]){FIRST_ROW + k}\b", "#", str(v)) for v in row) for k, row in enumerate(intake)}
    assert len(same) == 1
    assert ROSTER_SHEET in intake[0][0] and SUBJECT_SHEET in intake[0][0]
    formulas = [f for row in intake for f in row if isinstance(f, str) and f.startswith("=")]
    assert all("IMPORTRANGE" not in f for f in formulas)
    assert book.yellow[INTAKE_SHEET] == ["F4:H7"] and len(book.red[INTAKE_SHEET]) == 2


# ---------- 出席の自動計算（#12） ----------

CASES = [  # 授業数, 欠席, 遅刻
    (30, 0, 0), (30, 1, 0), (30, 0, 2), (30, 1, 1), (30, 2, 0), (30, 3, 1), (25, 1, 0), (25, 10, 0),
    (25, 9, 3), (30, 12, 0), (30, 11, 2), (45, 7, 5), (16, 3, 2), (30, 12, 1),
]
BAD = [(0, 0, 0), (None, 0, 0), (10, 11, 0)]


@needs_calc
@pytest.mark.parametrize("maximum", [10, 20])
def test_auto_attendance_matches_first_term_rule(tmp_path, maximum):
    ids = [f"S{i:02d}" for i in range(len(CASES) + len(BAD))]
    roster = [(sid, sid, "", "国際") for sid in ids]
    intake = [(sid, *c) for sid, c in zip(ids, CASES + BAD)]
    got = _recalc(_sub(slots=len(ids)), tmp_path, roster=roster, intake=intake, edits={"E2": maximum})
    for k, (n, a, late) in enumerate(CASES):
        assert got.cell(FIRST_ROW + k, 3).value == expected_points(n, a, late, maximum, maximum // 10), (n, a, late)
    for k in range(len(BAD)):
        assert got.cell(FIRST_ROW + len(CASES) + k, 3).value == "要確認"
