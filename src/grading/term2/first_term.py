"""後期の成績表の「前期成績」シート（白・値だけ）に写す中身を、前期の通知表と同じ計算（read_cards）から作る。

前期のファイルにはつながない。値として一度だけ写す。
例外処置（利用者の指示）: 行の評定欄に指定の文字を出し、点数・取得は空欄、単位は取得に数えない。
"""

from dataclasses import replace
from fractions import Fraction

from grading.export.report_card import Card

SHEET = "前期成績"
LINE_HEAD = ["学籍番号", "氏名", "学科", "科目", "形態", "点数", "評定", "設定単位", "取得単位"]
TOTAL_HEAD = ["学籍番号", "設定単位計", "取得単位計", "授業時数", "出席時数"]


def apply_exceptions(cards: list[Card], exceptions: dict[tuple[str, str], str]) -> list[Card]:
    """exceptions: (学籍番号, 通知表の科目名) → 評定欄に出す文字。見つからないものがあれば止める。"""
    left = dict(exceptions)
    out = []
    for c in cards:
        lines = []
        for l in c.lines:
            mark = left.pop((c.student_id, l.name), None)
            lines.append(l if mark is None else replace(l, withheld=True, withheld_grade=mark))
        out.append(replace(c, lines=tuple(lines)))
    if left:
        raise ValueError(f"例外処置の対象が見つからない: {sorted(left)}")
    return out


def _number(x: Fraction | float) -> float:
    return round(float(x), 10)


def sheet_rows(cards: list[Card]) -> tuple[list[list], list[list]]:
    """(科目ごとの行, 学生ごとの前期計の行)。点数は丸めずに写す（表示の丸めは通知表の側で行う）。"""
    lines = []
    totals = []
    for c in cards:
        for l in c.lines:
            lines.append([c.student_id, c.name_en, c.dept, l.name, l.kind,
                          None if l.withheld else l.score,
                          l.withheld_grade if l.withheld else l.grade,
                          l.credits, l.earned])
        totals.append([c.student_id, c.credits_set, c.credits_earned, c.hours, _number(c.attended)])
    return lines, totals
