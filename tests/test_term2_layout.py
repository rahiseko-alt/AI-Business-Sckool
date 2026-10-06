import re
import shutil
import subprocess
from fractions import Fraction

import pytest
from openpyxl import Workbook, load_workbook

from grading.rules.master import SubjectRule
from grading.term2.layout import (ATTENDANCE_COPY, CHECK_SHEET, EXCLUDE_SHEET, FIRST_ROW, INTAKE_SHEET,
                                  LINK_SHEET_ATTENDANCE, LINKS_SHEET, ROSTER_COPY, ROSTER_SHEET, SUBJECT_SHEET,
                                  SUBMISSION_TAB, SUBMITTED_CELL, SUMMARY_SHEET, gradebook_cells, master_cells,
                                  submission_cells)
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
    return _calc(wb, tmp_path)[SUBMISSION_TAB]


def _calc(wb, tmp_path):
    """LibreOffice で開いて再計算し、値だけの本を返す。"""
    src = tmp_path / "s.xlsx"
    wb.save(src)
    out = tmp_path / "out"
    subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp_path}/profile", "--headless", "--convert-to",
                    "xlsx:Calc MS Excel 2007 XML", "--outdir", str(out), str(src)],
                   check=True, capture_output=True, timeout=180)
    return load_workbook(out / "s.xlsx", data_only=True)


def _sheet(wb, title, rows, keep=lambda v: True):
    """rows をシートに書く。IMPORTRANGE の式（本物では他の表から入る）は書かずに空けておく。"""
    ws = wb.create_sheet(title)
    for r, row in enumerate(rows, 1):
        for c, v in enumerate(row, 1):
            if v is not None and "IMPORTRANGE" not in str(v) and keep(c):
                ws.cell(r, c, v.replace("TEXTJOIN(", "_xlfn.TEXTJOIN(") if isinstance(v, str) else v)
    return ws


def _recalc_summary(tmp_path, rows, thresholds=(80, 70, 60, 50), points=(30, 20, 50)):
    """集計の1科目ぶんを、取り込む欄（B〜F・見出しの配点と提出済み・J〜L）を値で置いて再計算する。
    rows: (学籍番号, 出席, 態度, テスト, 合計, 出席（手入力）)。"""
    book = gradebook_cells([("国際", "科目A")], slots=len(rows))
    wb = Workbook()
    wb.remove(wb.active)
    links = _sheet(wb, LINKS_SHEET, book.tabs[LINKS_SHEET])
    for k, v in enumerate(thresholds):
        links.cell(FIRST_ROW + k, 6, v)
    ws = _sheet(wb, SUMMARY_SHEET, book.tabs[SUMMARY_SHEET])
    for c, v in enumerate([*points, sum(points)], 3):
        ws.cell(FIRST_ROW, c, v)
    ws.cell(FIRST_ROW, 7, True)
    for k, (sid, *scores, manual) in enumerate(rows):
        for c, v in enumerate([sid, *scores], 2):
            ws.cell(FIRST_ROW + 1 + k, c, v)
        ws.cell(FIRST_ROW + 1 + k, 10, manual)
    return _calc(wb, tmp_path)[SUMMARY_SHEET]


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
    assert [r[0] for r in book.tabs[LINKS_SHEET][FIRST_ROW - 1:] if r[0]] == ["科目A", "科目A", "出席簿"]
    formulas = [f for row in book.tabs[SUMMARY_SHEET] for f in row if isinstance(f, str) and "IMPORTRANGE" in f]
    assert len(formulas) == 8                                              # 科目ごとに配点・提出済み・点・手入力
    assert all("docs.google.com" not in f for f in formulas)
    assert all(f"INDEX({LINKS_SHEET}!$B$4:$B$5," in f for f in formulas)     # つなぎ先一覧の何番目かで読む
    blocks = book.tabs[SUMMARY_SHEET][FIRST_ROW - 1:]
    assert len(blocks) == 2 * 4                                            # 見出し＋学生3行 が科目ぶん
    shift = lambda row, k: tuple(re.sub(rf"(?<=[A-Z]){FIRST_ROW + k}\b", "#", str(v)) for v in row)
    assert {shift(blocks[k], k) + shift(blocks[k + 1], k + 1) for k in (0, 4)} == {shift(blocks[0], 0) + shift(blocks[1], 1)}
    assert any("1,5,8,11,12" in f for f in formulas)
    assert any("'提出'!E2:L2\"),1,4,7,8)" in f for f in formulas)          # 配点3つと合計
    assert any("'提出'!A4:L6\"),4,7,10)" in f for f in formulas)           # 提出用の表の手入力
    assert book.yellow[LINKS_SHEET] == ["B4:B6", "F4:F7"]


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


# ---------- 評定・確認内容・確認シート ----------

def _rule(thresholds):
    grades = tuple(zip("ABCDE", [Fraction(t) for t in (*thresholds, 0)]))
    return SubjectRule("科目A", "", (), {}, grades, {}, {})


TOTALS = [100, 80, 79.9, 70, 69.5, 60, 50, 49.9, 0]


@needs_calc
@pytest.mark.parametrize("thresholds", [(80, 70, 60, 50), (90, 75, 60, 40)])
def test_grade_matches_first_term_rule(tmp_path, thresholds):
    rows = [(f"S{k:02d}", 10, 10, 10, t, None) for k, t in enumerate(TOTALS)] + [("S99", 10, 10, 10, None, None)]
    got = _recalc_summary(tmp_path, rows, thresholds)
    for k, t in enumerate(TOTALS):
        assert got.cell(FIRST_ROW + 1 + k, 8).value == _rule(thresholds).grade_for(Fraction(str(t))), t
    assert got.cell(FIRST_ROW + 1 + len(TOTALS), 8).value is None             # 合計が空なら評定も空


@needs_calc
@pytest.mark.parametrize("thresholds", [(None, None, None, None), (80, 70, None, 50), (70, 80, 60, 50),
                                        (80, 70, 60, 0), (80, 70, 70, 50)])
def test_grade_is_to_be_checked_when_thresholds_are_blank_or_out_of_order(tmp_path, thresholds):
    got = _recalc_summary(tmp_path, [("S01", 10, 10, 10, 75, None), ("S02", 10, 10, 10, 30, None)], thresholds)
    assert [got.cell(FIRST_ROW + k, 8).value for k in (1, 2)] == ["要確認", "要確認"]


@needs_calc
def test_grade_is_to_be_checked_when_a_part_is_missing(tmp_path):
    rows = [("S01", 10, None, 50, 60, None), ("S02", "要確認", 20, 50, 70, None), ("S03", 10, 20, 50, 80, None)]
    got = _recalc_summary(tmp_path, rows, (80, 70, 60, 50))
    assert [got.cell(FIRST_ROW + 1 + k, 8).value for k in range(3)] == ["要確認", "要確認", "A"]


@needs_calc
def test_summary_check_lists_what_is_wrong(tmp_path):
    rows = [("K01", 30, 20, 50, 100, None),     # 問題なし
            ("K02", 10, None, 50, 60, None),     # 提出済みなのに空欄
            ("K03", 31, 20, 40, 91, None),       # 配点超え
            ("K04", 10, -1, 40, 49, None),       # 負
            ("K05", 10, 20, "abc", 30, None),    # 数値でない
            ("K06", "要確認", 20, 40, 60, None),  # 出席の数がおかしい（点数がおかしいには数えない）
            (None, None, None, None, None, 5),   # 学生のいない行に手入力
            (None, None, None, None, None, None),  # 空の行
            ("K09", 31, None, 50, 81, None)]     # 2つ重なる
    got = _recalc_summary(tmp_path, rows)
    bad = "点数がおかしい（配点超え・負・数値でない）"
    assert [got.cell(FIRST_ROW + 1 + k, 9).value for k in range(len(rows))] == [
        None, "提出済みなのに空欄", bad, bad, bad, "出席の数がおかしい", "学生のいない行に手入力", None,
        f"提出済みなのに空欄・{bad}"]
    assert got.cell(FIRST_ROW + 7, 1).value == "科目A"                     # 手入力が残る行は科目名を出す
    assert got.cell(FIRST_ROW + 8, 1).value is None
    assert got.cell(FIRST_ROW, 9).value is None                            # 配点の合計が100


@needs_calc
def test_summary_header_flags_points_not_totalling_100(tmp_path):
    got = _recalc_summary(tmp_path, [("K01", 10, 10, 10, 30, None)], points=(30, 20, 40))
    assert got.cell(FIRST_ROW, 9).value == "配点の合計が100でない"


@needs_calc
@pytest.mark.parametrize("book_url", [None, "https://example.com/出席簿"])
def test_intake_check_flags_bad_counts_and_manual_entry_without_student(tmp_path, book_url):
    cases = [("K01", None, (30, 2, 1)), ("K02", None, (0, 0, 0)), ("K03", None, (None, None, None)),
             ("K04", None, (10, 10, 3)), ("K05", None, (10, -1, 0)), (None, 5, (5, 0, 0)), (None, None, (None,) * 3)]
    book = gradebook_cells([("国際", "科目A")], slots=len(cases))
    wb = Workbook()
    wb.remove(wb.active)
    ws = _sheet(wb, INTAKE_SHEET, book.tabs[INTAKE_SHEET], keep=lambda c: c == 12)
    links = wb.create_sheet(LINKS_SHEET)
    links.cell(FIRST_ROW + 1, 2, book_url)                                # 出席簿のアドレス（科目1つの次の行）
    for k, (sid, manual, counts) in enumerate(cases):
        r = FIRST_ROW + k
        ws.cell(r, 1, sid), ws.cell(r, 2, "科目A" if sid else None), ws.cell(r, 6, manual)
        for c, v in enumerate(counts, 9):
            ws.cell(r, c, v)
    got = _calc(wb, tmp_path)[INTAKE_SHEET]
    bad = "授業数・欠席・遅刻がおかしい"
    # 数が1つも無い行（K03）は、出席簿をつなぐまでは要確認にしない
    assert [got.cell(FIRST_ROW + k, 12).value for k in range(len(cases))] == [
        None, bad, bad if book_url else None, bad, bad, "学生のいない行に手入力", None]


@needs_calc
def test_points_total_is_not_red_until_teacher_starts(tmp_path):
    rule = dict(submission_cells("科目A", "担当", "国際", slots=1).red)["L2"]
    assert "COUNT($E$2,$H$2,$K$2)>0" in rule and "$F$1=TRUE" in rule


def test_check_sheet_counts_and_lists_from_summary_and_intake():
    book = gradebook_cells([("国際", "科目A"), ("総合", "科目A")], slots=3)
    check = book.tabs[CHECK_SHEET]
    assert check[0][0] == CHECK_SHEET
    # 集計の下端は 3＋2科目×(3＋1)＝11、出席の受け口は 3＋2×3＝9
    assert "MOD(ROW(集計!$A$4:$A$11)-4,4)=0" in check[2][1] and "集計!$G$4:$G$11<>TRUE" in check[2][1]
    assert "集計!$I$4:$I$11" in check[2][3] and "'出席の受け口'!$L$4:$L$9" in check[2][3]
    assert "設定!$F$7>0" in check[2][3] and "設定!$F$7>0" in check[2][5]
    assert "FILTER(集計!$A$4:$A$11," in check[5][0]
    assert "集計!$I$4:$I$11<>\"\"" in check[5][2] and "'出席の受け口'!$L$4:$L$9<>\"\"" in check[5][6]
    assert [r for r, _ in book.red[CHECK_SHEET]] == ["B3", "D3", "F3", "A6:A1000", "C6:E1000", "G6:I1000", "K6:M1000"]
    links = book.tabs[LINKS_SHEET]
    assert [links[r][4] for r in range(2, 8)] == ["評定", "A", "B", "C", "D", "E"]
    assert [links[r][5] for r in range(3, 8)] == [None, None, None, None, 0]
    assert book.red[LINKS_SHEET][0][0] == "F4:F7" and "F4:F7" in book.yellow[LINKS_SHEET]
