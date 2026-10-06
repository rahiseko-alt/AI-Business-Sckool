"""後期バージョンの Google スプレッドシートの中身（セルの値と式・黄色の範囲）を組み立てる。

ここは「何をどのセルに置くか」だけを決める。実際に Google ドライブへ書き込むのは別（コネクタ経由）。
色の決まり（ADR 0003）: 黄＝人が入力、白＝式、赤＝要確認。
成績表が提出用の表を読むときは、必ず「設定」シートのつなぎ先一覧のアドレスを経由する
（学校のアカウントへ移したとき、そこを貼り直すだけで済むように）。
"""

from dataclasses import dataclass, field

SUBMISSION_TAB = "提出"
LINKS_SHEET = "設定"
FIRST_ROW = 4          # 学生の行の開始（1〜3行目は題名と見出し）


@dataclass
class Cells:
    values: list[list]
    yellow: list[str] = field(default_factory=list)


@dataclass
class Book:
    tabs: dict[str, list[list]]
    yellow: dict[str, list[str]] = field(default_factory=dict)


def submission_cells(subject: str, student_ids: list[str]) -> Cells:
    """提出用の表（最小）: 学籍番号と点数。点数の欄が黄色。"""
    rows = [[f"提出用の表　{subject}", None], [None, None], ["学籍番号", "点数"]]
    rows += [[sid, None] for sid in student_ids]
    last = FIRST_ROW + len(student_ids) - 1
    return Cells(rows, [f"B{FIRST_ROW}:B{last}"])


def gradebook_cells(subjects: list[str], rows: int) -> Book:
    """成績表（最小）: 設定のつなぎ先一覧（黄）と、それを経由して提出用の表を読む集計。"""
    links = [["つなぎ先一覧", None], ["提出用の表のアドレスを貼る。学校のアカウントへ移したら、ここだけ貼り直す", None],
             ["科目", "アドレス"]]
    links += [[s, None] for s in subjects]
    summary = [["集計", None], [None, None], ["学籍番号", "点数"]]
    last = FIRST_ROW + rows - 1
    for k, _ in enumerate(subjects):
        url = f"{LINKS_SHEET}!$B${FIRST_ROW + k}"
        summary.append([f"=IMPORTRANGE({url},\"'{SUBMISSION_TAB}'!A{FIRST_ROW}:B{last}\")", None])
    return Book({LINKS_SHEET: links, "集計": summary},
                {LINKS_SHEET: [f"B{FIRST_ROW}:B{FIRST_ROW + len(subjects) - 1}" if len(subjects) > 1 else f"B{FIRST_ROW}"]})
