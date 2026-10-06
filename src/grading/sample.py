"""架空データで成績資料の見本を作る。実在の学生・資料とは無関係。

    python3 -m grading.sample docs/sample      # Excel・HTML・PDF（Chromium があれば）を作る
"""

import shutil
import subprocess
import sys
from pathlib import Path

from grading.calculation import ItemValue, calculate
from grading.domain.enums import DataStatus
from grading.export import check_finalizable
from grading.export.report_html import write_html_report
from grading.export.workbook import Entry, EvidenceRef, Notice, write_workbook
from grading.identity import IdentityClaim, Student, resolve
from grading.normalization import parse_value
from grading.rules import RuleBook, SubjectRule
from grading.validation import completeness_matrix

STUDENTS = [
    Student("S001", "20260031", "山田 花子", "1A", 14),
    Student("S002", "20260082", "山田 花子", "1B", 8),
    Student("S003", "20260050", "佐藤 一郎", "1A", 20),
]

RULES = RuleBook([
    SubjectRule.from_dict({
        "subject": "AI基礎", "rule_ref": "採点基準.xlsx / AI基礎",
        "components": [{"name": "出席", "weight": 20, "items": ["出席回数"]},
                       {"name": "課題", "weight": 40, "items": ["課題1", "課題2", "課題3"]},
                       {"name": "試験", "weight": 40, "items": ["期末試験"]}],
        "max_scores": {"出席回数": 15, "課題1": 10, "課題2": 10, "課題3": 10, "期末試験": 100},
        "grade_thresholds": [["A", 90], ["B", 80], ["C", 70], ["D", 60], ["E", 0]],
        "markers": {"未提出": "NOT_SUBMITTED"},
        "value_policies": {"NOT_SUBMITTED": "SCORE_ZERO"},
    }),
    SubjectRule.from_dict({
        "subject": "マーケティング", "rule_ref": "シラバス_マーケティング.pdf p.3",
        "components": [{"name": "課題", "weight": 50, "items": ["レポート1", "レポート2"]},
                       {"name": "発表", "weight": 30, "items": ["発表"]},
                       {"name": "参加", "weight": 20, "items": ["参加"]}],
        "max_scores": {"レポート1": 20, "レポート2": 20, "発表": 30, "参加": 10},
        "grade_thresholds": [["A", 90], ["B", 80], ["C", 70], ["D", 60], ["E", 0]],
        "markers": {"対象外": "NOT_APPLICABLE"},
        "value_policies": {"NOT_APPLICABLE": "EXCLUDE"},
    }),
])

# (資料, シート, 列, 行の識別情報, {項目: 値})。行番号はセル番地に使う。
SOURCE_ROWS = [
    ("AI基礎_出席.xlsx", "1学期", "G", [
        (12, IdentityClaim("20260031", "山田 花子"), {"出席回数": 15}),
        (13, IdentityClaim("20260082", "山田　花子"), {"出席回数": 12}),
        (14, IdentityClaim("20260050", "佐藤 一郎"), {"出席回数": 14}),
    ]),
    ("AI基礎_課題一覧.xlsx", "課題", "H", [
        (31, IdentityClaim("20260031", "山田 花子"), {"課題1": 8, "課題2": 9, "課題3": 10}),
        (32, IdentityClaim("20260082", "山田 花子"), {"課題1": 7, "課題2": "未提出", "課題3": 9}),
        (33, IdentityClaim("20260050", "佐藤 一郎"), {"課題1": 6, "課題2": 7, "課題3": 8}),
    ]),
    ("AI基礎_試験.xlsx", "期末", "C", [
        (14, IdentityClaim("20260031", "山田 花子"), {"期末試験": 84}),
        (15, IdentityClaim("20260082", "山田 花子"), {"期末試験": 71}),
        (16, IdentityClaim("20260050", "佐藤 一郎"), {"期末試験": 62}),
    ]),
    ("マーケ_評価表.xlsx", "成績", "D", [
        (5, IdentityClaim("20260031", "山田 花子"), {"レポート1": 18, "レポート2": 15, "発表": 22, "参加": 9}),
        (6, IdentityClaim(name="山田 花子"), {"レポート1": 14, "レポート2": 16, "発表": 25, "参加": 8}),
        (7, IdentityClaim("20260050", "佐藤 一郎"), {"レポート1": 12, "レポート2": "対象外", "発表": 20, "参加": 7}),
    ]),
]

SUBJECT_OF = {"AI基礎_出席.xlsx": "AI基礎", "AI基礎_課題一覧.xlsx": "AI基礎", "AI基礎_試験.xlsx": "AI基礎",
              "マーケ_評価表.xlsx": "マーケティング"}


def _inputs() -> dict:
    evidence: dict[str, EvidenceRef] = {}
    owner: dict[str, str] = {}
    values: dict[tuple[str, str], list[ItemValue]] = {}
    notices: list[Notice] = []
    blocked_values: list[tuple[str, list[str], ItemValue]] = []

    for file_name, sheet, first_col, rows in SOURCE_ROWS:
        subject = SUBJECT_OF[file_name]
        rule = RULES.get(subject)
        for row, claim, items in rows:
            match = resolve(claim, STUDENTS)
            for offset, (item, raw) in enumerate(items.items()):
                col = chr(ord(first_col) + offset)
                eid = f"{file_name}!{sheet}!{col}{row}"
                evidence[eid] = EvidenceRef(file_name, sheet, f"{col}{row}")
                v = ItemValue(item, parse_value(raw, rule.markers), eid, match.data_status)
                if match.student_key is None:
                    blocked_values.append((subject, list(match.candidates), v))
                    continue
                owner[eid] = match.student_key
                values.setdefault((match.student_key, subject), []).append(v)
            if match.student_key is None:
                cands = "、".join(f"{s.student_number}/{s.class_}/{s.name}" for s in STUDENTS
                                 if s.student_key in match.candidates)
                notices.append(Notice("停止", f"資料「{file_name}」の{row}行目「{claim.name}」は学籍番号が無く、"
                                            f"同姓同名が複数います（{cands}）。どの学生ですか？", subject=subject))
            elif match.data_status == DataStatus.WARNING:
                notices.append(Notice("要確認", f"資料「{file_name}」の{row}行目: {'、'.join(match.reasons)}",
                                      match.student_key, subject))

    expected = {(s.student_key, sub) for s in STUDENTS for sub in RULES.subjects()}
    entries, results = [], {}
    for key, subject in sorted(expected):
        vals = values.get((key, subject), [])
        out = calculate(key, RULES.get(subject), vals)
        if isinstance(out, list):
            entries.append(Entry(key, subject, vals, None, out))
        else:
            entries.append(Entry(key, subject, vals, out))
            results[(key, subject)] = (out, vals)

    matrix = completeness_matrix([s.student_key for s in STUDENTS], RULES.subjects(), expected,
                                 {k: r.status for k, (r, _) in results.items()})
    report = check_finalizable(open_blockers=sum(n.level == "停止" for n in notices), matrix=matrix,
                               results=results, rules=RULES, evidence_owner=owner.get)
    return dict(students={s.student_key: s for s in STUDENTS}, rules=RULES, entries=entries, matrix=matrix,
                report=report, locate=evidence.__getitem__, notices=notices, evidence_owner=owner.get)


def build(path: str | Path) -> Path:
    data = _inputs()
    data.pop("evidence_owner")
    return write_workbook(path, **data)


def build_html(path: str | Path) -> Path:
    return write_html_report(path, title="成績資料（見本・架空データ）", **_inputs())


CHROME = shutil.which("chromium") or "/opt/pw-browsers/chromium"


def html_to_pdf(html_path: Path, pdf_path: Path) -> Path:
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()],
                   check=True, capture_output=True, timeout=120)
    return pdf_path


def build_all(directory: str | Path) -> list[Path]:
    directory = Path(directory)
    made = [build(directory / "成績資料_サンプル.xlsx"), build_html(directory / "成績資料_サンプル.html")]
    if Path(CHROME).exists():
        made.append(html_to_pdf(made[1], directory / "成績資料_サンプル.pdf"))
    return made


if __name__ == "__main__":
    for p in build_all(sys.argv[1] if len(sys.argv) > 1 else "data/output"):
        print(p)
