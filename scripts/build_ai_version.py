"""成績表のAI計算版を作る。2026年度前期。

    python3 scripts/build_ai_version.py

出力は両学科で1ファイル（data/output/成績表_2026前期_AI計算版.xlsx）。シート:
  AI計算版_国際／AI計算版_総合／原本_国際／原本_総合／E一覧_国際／E一覧_総合／E一覧_統合／個人別評定_国際／個人別評定_総合／
  テスト分析／偏差値
AI計算版は原本を丸ごと写し、次のセルだけをAIの計算値に置き換える（色付き）。それ以外は原本のまま（合計等の式も残る）。
出席点の横にある出席率の列も、出席簿から計算した率（丸めない）に置き換える。
E一覧と個人別評定は、AI計算版を LibreOffice で再計算した値から作る。
入力は data/input/（Git 対象外）。ここに書いた決まりは、すべて利用者の回答（data/input/decisions.json）による。
- 出席点（7科目）: 出席簿だけから計算。出席率＝1−（欠＋遅÷3）÷授業数（出席簿にある式）。4%ごとに減点、60%未満は0点
  - 日本語運用力強化演習は1週＝1回（その週に1回でも出席なら出席）
  - 国際5月 CE3 の「4月26日」は5月26日
- 態度点: 百井先生の3科目は 10−2×遅刻（出席簿の「遅」）。テキスト忘れ等の名前つき記録は0件
          浅田先生（理論）は 10−1×（私語・居眠り・スマホの名前つき記録0件）。遅刻は引かない
          樋口先生の3科目は計算しない（原本のまま）
"""

import datetime as dt
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

from openpyxl import Workbook, load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from grading.analysis.sheets import add_deviation_sheet, add_test_analysis, collect_tests  # noqa: E402
from grading.export.copy_sheet import copy_sheet  # noqa: E402
from grading.export.e_list import add_e_matrix, add_personal_grades, gpa_of, grade_rows  # noqa: E402
from grading.export.fill import FilledValue, apply_ai_values, apply_rates, rate_columns  # noqa: E402
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


SCHEDULE = {  # 評価表①②③の授業曜日と担当。学科で違う科目は学科名で分ける
    "ビジネス日本語": ("樋口", "月"), "マーケティング": ("百井", "月"),
    "ビジネスプレゼンテーション": ("元島", "火"), "AI演習（実践）": ("百井", "火"),
    "就職指導キャリアガイダンス": ("元島", "水"), "ビジネス演習（理論）": ("浅田", "水"),
    "ビジネス演習（実践）": ("元島", "木"), "日本語能力強化演習": ("樋口", "木"),
    "ビジネス情報リテラシー": ("百井", "金"), "国際理解": ("元島", "金"), "総合ビジネス概論": ("元島", "金"),
}
SCHEDULE_BY_DEPT = {
    "国際ビジネス科": {"キャリア形成演習": ("元島", "水"), "日本語運用力強化演習": ("樋口", "月・火")},
    "総合ビジネス科": {"キャリア形成演習": ("百井", "月"), "日本語運用力強化演習": ("樋口", "火・水")},
}
DEPT_SHORT = {"国際ビジネス科": "国際", "総合ビジネス科": "総合"}
OUTPUT = DATA / "output" / "成績表_2026前期_AI計算版.xlsx"


def counts_of(register_name: str):
    reg = read_register(DATA / "input" / register_name, date_corrections=DATE_CORRECTIONS)
    counts = subject_counts(reg)
    counts.update(weekly_counts(reg, WEEKLY))
    return counts


def ai_values(register_name: str, original_ws) -> list[FilledValue]:
    counts = counts_of(register_name)
    students = [str(original_ws.cell(r, 2).value).strip() for r in range(6, original_ws.max_row + 1)
                if original_ws.cell(r, 2).value]
    values = []
    for subject, (maximum, step) in ATTENDANCE.items():
        unit = "週" if subject == WEEKLY else "回"
        for sid in students:
            n = counts[(sid, subject)]
            points, how = attendance_points(n.rate, maximum, step)
            values.append(FilledValue(sid, subject, "出席", points,
                                      f"授業{n.sessions}{unit}・欠席{n.absent}・遅刻{n.late} → {how}",
                                      n.absent_cells + n.late_cells))
    for subject in MOMOI:
        for sid in students:
            n = counts[(sid, subject)]
            values.append(FilledValue(sid, subject, "授業態度", Fraction(10 - 2 * n.late),
                                      f"10 − 2 × 遅刻{n.late}回", n.late_cells))
    for sid in students:
        values.append(FilledValue(sid, "ビジネス演習(理論)", "授業態度", Fraction(10),
                                  "10 − 1 × 私語・居眠り・スマホ0回（遅刻は引かない）", ()))
    return values


def recalculated(path: Path):
    """LibreOffice で再計算した値のブックを返す。"""
    if not shutil.which("soffice"):
        raise RuntimeError("LibreOffice（soffice）が無いため、E一覧と個人別評定を作れない")
    tmp = tempfile.mkdtemp()
    src = Path(tmp) / "in.xlsx"
    shutil.copy(path, src)
    subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp}/profile", "--headless", "--convert-to",
                    "xlsx:Calc MS Excel 2007 XML", "--outdir", f"{tmp}/out", str(src)],
                   check=True, capture_output=True, timeout=300)
    return load_workbook(Path(tmp) / "out" / "in.xlsx", data_only=True)


def build_all() -> Path:
    wb = Workbook()
    wb.remove(wb.active)
    for register_name, original_name, dept in DEPTS:
        short = DEPT_SHORT[dept]
        original = load_workbook(DATA / "input" / original_name).worksheets[0]
        ai = copy_sheet(original, wb, f"AI計算版_{short}")
        if isinstance(ai["A1"].value, str):
            ai["A1"].value += "（AI計算版）"
        apply_ai_values(ai, ai_values(register_name, original))
        # 出席点の横にある出席率の列も、出席簿から計算した率にそろえる（原本の率が残ると食い違って見えるため）
        counts = counts_of(register_name)
        apply_rates(ai, rate_columns(original), {k: v.rate for k, v in counts.items() if k[1] in ATTENDANCE})
    for register_name, original_name, dept in DEPTS:
        copy_sheet(load_workbook(DATA / "input" / original_name).worksheets[0], wb, f"原本_{DEPT_SHORT[dept]}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT)

    values = recalculated(OUTPUT)
    groups = []
    for _, _, dept in DEPTS:
        sheet = values[f"AI計算版_{DEPT_SHORT[dept]}"]
        groups.append((dept, grade_rows(sheet), {**SCHEDULE, **SCHEDULE_BY_DEPT[dept]}, gpa_of(sheet)))
    for dept, rows, info, _ in groups:
        add_e_matrix(wb, [(dept, rows, info)], f"E一覧_{DEPT_SHORT[dept]}")
    add_e_matrix(wb, [(d, r, i) for d, r, i, _ in groups], "E一覧_統合")
    for dept, rows, _, gpa in groups:
        add_personal_grades(wb, rows, gpa, title=f"個人別評定_{DEPT_SHORT[dept]}")   # GPA評定は基準が未定のため空欄
    tests = [t for _, _, dept in DEPTS for t in collect_tests(values[f"AI計算版_{DEPT_SHORT[dept]}"], dept)]
    add_test_analysis(wb, tests)
    add_deviation_sheet(wb, tests)
    wb.save(OUTPUT)
    for old in DATA.joinpath("output").glob("成績表_*ビジネス科_AI計算版*.xlsx"):
        old.unlink()
    return OUTPUT


if __name__ == "__main__":
    print(build_all())
