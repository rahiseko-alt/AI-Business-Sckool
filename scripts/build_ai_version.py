"""成績表のAI計算版を作る。2026年度前期。

    python3 scripts/build_ai_version.py

出力は1学科1ファイル。シートは「AI計算版」「原本」「計算根拠_先生名」。
AI計算版は原本を丸ごと写し、次のセルだけをAIの計算値に置き換える（色付き）。それ以外は原本のまま（合計等の式も残る）。
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

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from grading.export.basis import BasisRow, add_teacher_basis  # noqa: E402
from grading.export.e_list import add_e_list, grade_rows  # noqa: E402
from grading.export.fill import FilledValue, build_ai_workbook  # noqa: E402
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


TEACHER = {"ビジネス日本語": "樋口", "日本語運用力強化演習": "樋口", "日本語能力強化演習": "樋口",
           "マーケティング": "百井", "AI演習": "百井", "ビジネス情報リテラシー": "百井", "ビジネス演習(理論)": "浅田"}


def build(register_name: str, original_name: str, dept: str) -> Path:
    reg = read_register(DATA / "input" / register_name, date_corrections=DATE_CORRECTIONS)
    counts = subject_counts(reg)
    counts.update(weekly_counts(reg, WEEKLY))
    original = load_workbook(DATA / "input" / original_name).worksheets[0]
    students = [str(original.cell(r, 2).value).strip() for r in range(6, original.max_row + 1) if original.cell(r, 2).value]
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
    for sid in students:
        values.append(FilledValue(sid, "ビジネス演習(理論)", "授業態度", Fraction(10),
                                  "10 − 1 × 私語・居眠り・スマホ0回 = 10（授業報告に名前つきの記録なし。遅刻は引かない）",
                                  ("授業報告 全期間",)))
    old = DATA / "output" / f"成績表_{dept}_AI計算版_入力済.xlsx"
    if old.exists():
        old.unlink()
    names = {str(original.cell(r, 2).value).strip(): original.cell(r, 3).value
             for r in range(6, original.max_row + 1) if original.cell(r, 2).value}
    by = {(v.student_id, v.subject, v.item): v.value for v in values}

    def basis(wb):
        for teacher in dict.fromkeys(TEACHER.values()):
            subjects = [s for s, t in TEACHER.items() if t == teacher]
            rows = []
            for sid in students:
                for subject in subjects:
                    n = counts[(sid, subject)]
                    rows.append(BasisRow(sid, names[sid], subject, n.sessions, n.absent, n.late, n.rate,
                                         by[(sid, subject, "出席")], by.get((sid, subject, "授業態度"))))
            add_teacher_basis(wb, teacher, subjects, rows)

    return build_ai_workbook(DATA / "input" / original_name, DATA / "output" / f"成績表_{dept}_AI計算版.xlsx",
                             values, TEACHER, evidence=False, extra=basis)


def add_e_sheet(path: Path) -> int:
    """LibreOffice で再計算した値から評定Eの一覧を作り、同じファイルに「E一覧」シートとして足す。"""
    if not shutil.which("soffice"):
        raise RuntimeError("LibreOffice（soffice）が無いため、E一覧を作れない")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "in.xlsx"
        shutil.copy(path, src)
        subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp}/profile", "--headless", "--convert-to",
                        "xlsx:Calc MS Excel 2007 XML", "--outdir", f"{tmp}/out", str(src)],
                       check=True, capture_output=True, timeout=300)
        rows = grade_rows(load_workbook(Path(tmp) / "out" / "in.xlsx", data_only=True)["AI計算版"])
    wb = load_workbook(path)
    add_e_list(wb, rows)
    wb.save(path)
    return sum(1 for r in rows if r.grade == "E")


if __name__ == "__main__":
    for args in DEPTS:
        out = build(*args)
        print(out, "E:", add_e_sheet(out))
