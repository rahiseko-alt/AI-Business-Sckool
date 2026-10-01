"""学校の成績表（出力の形）から、値と計算式をすべて消した白紙のコピーを作る。

残すもの: 見出し（1〜4行目）、評価項目名のある列の点数配分（5行目の数値）、学生の NO.・学籍番号・氏名・日本名、書式。
消すもの: 学生行の E 列以降すべて、5行目の計算式と見出しの無い補助列の値、その他すべての計算式。
元のファイルには触れない。
"""

from pathlib import Path

from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell

HEADER_ROW_ITEMS = 4      # 評価項目名の行
ALLOCATION_ROW = 5        # 点数配分の行
FIRST_STUDENT_ROW = 6
FIRST_VALUE_COL = 5       # E列
STUDENT_ID_COL = 2        # B列（学籍番号）
AI_MARK = "（AI計算版）"


def _is_formula(value: object) -> bool:
    return isinstance(value, str) and value.startswith("=") or type(value).__name__ in ("ArrayFormula", "DataTableFormula")


def blank_template(src: str | Path, dst: str | Path) -> Path:
    wb = load_workbook(src)
    for ws in wb.worksheets:
        for row in range(FIRST_STUDENT_ROW, ws.max_row + 1):
            if ws.cell(row, STUDENT_ID_COL).value is None:
                continue
            for col in range(FIRST_VALUE_COL, ws.max_column + 1):
                if not isinstance(ws.cell(row, col), MergedCell):
                    ws.cell(row, col).value = None
        for col in range(FIRST_VALUE_COL, ws.max_column + 1):
            cell = ws.cell(ALLOCATION_ROW, col)
            if isinstance(cell, MergedCell):
                continue
            if _is_formula(cell.value) or ws.cell(HEADER_ROW_ITEMS, col).value is None:
                cell.value = None
        for row in ws.iter_rows():
            for cell in row:
                if _is_formula(cell.value) and not isinstance(cell, MergedCell):
                    cell.value = None
        title = ws["A1"]
        if isinstance(title.value, str) and not title.value.endswith(AI_MARK):
            title.value += AI_MARK
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    return dst
