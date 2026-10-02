"""科目ごとの評定E一覧。再計算済みの成績表（値）から読む。

その学生の評価項目がすべて空欄の科目（受講していない科目）は一覧に入れない。
"""

from collections.abc import Sequence
from dataclasses import dataclass

from openpyxl.styles import Font, PatternFill


@dataclass(frozen=True)
class GradeRow:
    subject: str
    student_id: str
    name: str
    total: object
    grade: object
    kana: str = ""


def _kana(value) -> str:
    return " ".join(str(value or "").replace("\n", " ").replace("\u3000", " ").split())


def grade_rows(ws) -> list[GradeRow]:
    groups, current = [], None
    for c in range(5, ws.max_column + 1):
        head = ws.cell(3, c).value
        if isinstance(head, str) and head.strip():
            current = {"subject": head.strip(), "items": [], "total": None, "grade": None}
            groups.append(current)
        item = ws.cell(4, c).value
        if current is None or not isinstance(item, str):
            continue
        if item.strip() == "合計":
            current["total"] = c
        elif item.strip() == "評定":
            current["grade"] = c
        elif current["total"] is None:
            current["items"].append(c)
    out = []
    for g in groups:
        if g["grade"] is None:
            continue
        for r in range(6, ws.max_row + 1):
            sid = ws.cell(r, 2).value
            if not sid:
                continue
            if all(ws.cell(r, c).value in (None, "") for c in g["items"]):
                continue
            out.append(GradeRow(g["subject"], str(sid).strip(), ws.cell(r, 3).value,
                                ws.cell(r, g["total"]).value if g["total"] else None, ws.cell(r, g["grade"]).value,
                                _kana(ws.cell(r, 4).value)))
    return out


_HEAD = PatternFill("solid", fgColor="DDE7F3")
_E = PatternFill("solid", fgColor="F8CBAD")


def _bold(row):
    for cell in row:
        cell.font, cell.fill = Font(bold=True), _HEAD


def add_e_list(wb, rows: Sequence[GradeRow], subject_info: dict[str, tuple[str, str]] | None = None):
    """追試の予定を立てやすい形のE一覧を2枚作る。subject_info: 科目 → (担当, 曜日)。

    「E一覧」: Eのある学生×科目の表。セルにはその科目の合計点。担当と曜日を見出しに置き、E科目数の多い順。
    「E一覧_科目別」: 科目ごとにEの学生を並べる（担当・曜日つき）。
    """
    info = subject_info or {}
    es = [r for r in rows if r.grade == "E"]
    subjects = [s for s in dict.fromkeys(r.subject for r in rows) if any(e.subject == s for e in es)]
    per_student: dict[str, list[GradeRow]] = {}
    for e in es:
        per_student.setdefault(e.student_id, []).append(e)
    order = sorted(per_student, key=lambda sid: (-len(per_student[sid]), sid))

    ws = wb.create_sheet("E一覧")
    fixed = ["学籍番号", "氏名", "カタカナ", "E科目数"]
    ws.append(["科目", "", "", "", *subjects])
    ws.append(["担当", "", "", "", *[info.get(s, ("", ""))[0] for s in subjects]])
    ws.append(["曜日", "", "", "", *[info.get(s, ("", ""))[1] for s in subjects]])
    ws.append(["Eの人数", "", "", len(es), *[sum(1 for e in es if e.subject == s) for s in subjects]])
    ws.append([*fixed, *["合計点" for _ in subjects]])
    for r in range(1, 6):
        _bold(ws[r])
    for sid in order:
        first = per_student[sid][0]
        by = {e.subject: e.total for e in per_student[sid]}
        ws.append([sid, first.name, first.kana, len(per_student[sid]), *[by.get(s) for s in subjects]])
        for k, s in enumerate(subjects):
            if s in by:
                ws.cell(ws.max_row, 5 + k).fill = _E
    for col, width in zip("ABCD", (12, 30, 24, 8)):
        ws.column_dimensions[col].width = width
    ws.freeze_panes = "E6"

    by_subject = wb.create_sheet("E一覧_科目別")
    by_subject.append(["科目", "担当", "曜日", "学籍番号", "氏名", "カタカナ", "合計点", "この学生のE科目数"])
    _bold(by_subject[1])
    for s in subjects:
        teacher, day = info.get(s, ("", ""))
        for e in sorted((e for e in es if e.subject == s), key=lambda e: e.student_id):
            by_subject.append([s, teacher, day, e.student_id, e.name, e.kana, e.total, len(per_student[e.student_id])])
    for col, width in zip("ABCDEFGH", (28, 8, 10, 12, 30, 24, 8, 10)):
        by_subject.column_dimensions[col].width = width
    by_subject.freeze_panes = "A2"
    return ws


def gpa_of(ws) -> dict[str, object]:
    """3行目が「GPA」の列から、学籍番号ごとのGPA（再計算済みの値）を読む。"""
    col = next((c for c in range(1, ws.max_column + 1) if str(ws.cell(3, c).value or "").strip() == "GPA"), None)
    if col is None:
        return {}
    return {str(ws.cell(r, 2).value).strip(): ws.cell(r, col).value for r in range(6, ws.max_row + 1) if ws.cell(r, 2).value}


def add_personal_grades(wb, rows: Sequence[GradeRow], gpa: dict[str, object], gpa_grade=None, title: str = "個人別評定"):
    """学生ごとに科目の評定とGPAだけを並べる。受講していない科目は「—」。gpa_grade は GPA→評定 の関数（未定なら空欄）。"""
    subjects = list(dict.fromkeys(r.subject for r in rows))
    students = list(dict.fromkeys((r.student_id, r.name, r.kana) for r in rows))
    grade = {(r.student_id, r.subject): r.grade for r in rows}
    ws = wb.create_sheet(title)
    ws.append(["学籍番号", "氏名", "カタカナ", *subjects, "GPA", "GPA評定"])
    for cell in ws[1]:
        cell.font, cell.fill = Font(bold=True), PatternFill("solid", fgColor="DDE7F3")
    for sid, name, kana in students:
        g = gpa.get(sid)
        ws.append([sid, name, kana, *[grade.get((sid, s), "—") for s in subjects], g,
                   gpa_grade(g) if gpa_grade and isinstance(g, (int, float)) else None])
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 24
    ws.freeze_panes = "D2"
    return ws
