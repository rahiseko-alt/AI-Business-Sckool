"""成績表のAI計算版（出席点・態度点）を作る。2026年度前期。

    python3 scripts/build_ai_version.py

入力は data/input/（Git 対象外）。ここに書いた決まりは、すべて利用者の回答（data/input/decisions.json）による。
- 出席点: 出席簿だけから計算。出席率＝1−（欠＋遅÷3）÷授業数（出席簿にある式）。4%ごとに減点、60%未満は0点
  - 日本語運用力強化演習は1週＝1回（その週に1回でも出席なら出席）
  - 国際5月 CE3 の「4月26日」は5月26日
- 態度点: 百井先生の3科目は 10−2×遅刻（出席簿の「遅」）。テキスト忘れ等の名前つき記録は0件
          樋口先生の3科目は元の成績表の値をそのまま採用（計算禁止）
          浅田先生・元島先生の科目は入れない（未決）
"""

import datetime as dt
import sys
from fractions import Fraction
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from grading.export.fill import FilledValue, _columns, fill_template  # noqa: E402
from grading.export.template import blank_template  # noqa: E402
from grading.importing.attendance import read_register, subject_counts, weekly_counts  # noqa: E402
from grading.rules.attendance_points import attendance_points  # noqa: E402

DATA = ROOT / "data"
DATE_CORRECTIONS = {"国際ビジネスAI科 5月!CE3": dt.date(2026, 5, 26)}
DEPTS = [  # (出席簿, 元の成績表, 学科名)
    ("attendance_kokusai.xlsx", "file3_ai.xlsx", "国際ビジネス科"),
    ("attendance_sougou.xlsx", "file4.xlsx", "総合ビジネス科"),
]
ATTENDANCE = {  # 科目: (満点, 4%ごとの減点)
    "ビジネス日本語": (10, 1), "マーケティング": (10, 1), "AI演習": (10, 1), "日本語運用力強化演習": (10, 1),
    "ビジネス演習(理論)": (20, 2), "日本語能力強化演習": (10, 1), "ビジネス情報リテラシー": (10, 1),
}
WEEKLY = "日本語運用力強化演習"
MOMOI = ["マーケティング", "AI演習", "ビジネス情報リテラシー"]
HIGUCHI = ["ビジネス日本語", "日本語運用力強化演習", "日本語能力強化演習"]


def build(register_name: str, original_name: str, dept: str) -> Path:
    reg = read_register(DATA / "input" / register_name, date_corrections=DATE_CORRECTIONS)
    counts = subject_counts(reg)
    counts.update(weekly_counts(reg, WEEKLY))
    original = load_workbook(DATA / "input" / original_name).worksheets[0]
    columns = _columns(original)
    students = {str(original.cell(r, 2).value).strip(): r for r in range(6, original.max_row + 1) if original.cell(r, 2).value}
    values = []
    for subject, (maximum, step) in ATTENDANCE.items():
        unit = "週" if subject == WEEKLY else "回"
        for sid in students:
            n = counts[(sid, subject)]
            points, how = attendance_points(n.rate, maximum, step)
            values.append(FilledValue(
                sid, subject, "出席", points,
                f"授業{n.sessions}{unit}・欠席{n.absent}・遅刻{n.late}（遅刻3回で欠席1回）→ {how}",
                n.absent_cells + n.late_cells or ("欠席・遅刻なし",)))
    for subject in MOMOI:
        for sid in students:
            n = counts[(sid, subject)]
            v = Fraction(10 - 2 * n.late)
            values.append(FilledValue(sid, subject, "授業態度", v,
                                      f"10 − 2 × 遅刻{n.late}回 − 2 × テキスト忘れ等0回 = {v}",
                                      n.late_cells or ("出席簿に遅刻なし",)))
    for subject in HIGUCHI:
        col = columns[(subject, "授業態度")]
        for sid, r in students.items():
            v = original.cell(r, col).value
            if not isinstance(v, int):
                raise ValueError(f"元の成績表の {sid} {subject} 授業態度が数値でない: {v!r}")
            values.append(FilledValue(sid, subject, "授業態度", Fraction(v),
                                      "元の成績表の値をそのまま採用（樋口先生の授業は態度点を計算しない）",
                                      (f"元の成績表!{get_column_letter(col)}{r}",)))
    blank = blank_template(DATA / "input" / original_name, DATA / "output" / f"成績表_{dept}_AI計算版.xlsx")
    return fill_template(blank, DATA / "output" / f"成績表_{dept}_AI計算版_入力済.xlsx", values)


if __name__ == "__main__":
    for args in DEPTS:
        print(build(*args))
