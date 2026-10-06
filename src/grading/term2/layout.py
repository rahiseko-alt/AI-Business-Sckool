"""後期バージョンの Google スプレッドシートの中身（セルの値と式・黄色の範囲・赤の条件）を組み立てる。

ここは「何をどのセルに置くか」だけを決める。実際に Google ドライブへ書き込むのは別（コネクタ経由）。
色の決まり（ADR 0003）: 黄＝人が入力、白＝式（保護付き）、赤＝要確認。
成績表が提出用の表を読むときは、必ず「設定」シートのつなぎ先一覧のアドレスを経由する
（学校のアカウントへ移したとき、そこを貼り直すだけで済むように）。
"""

from dataclasses import dataclass, field

SUBMISSION_TAB = "提出"
LINKS_SHEET = "設定"
FIRST_ROW = 4          # 学生の行の開始（1行目＝科目名・担当・提出済み、2行目＝配点、3行目＝見出し）
SUBMITTED_CELL = "F1"  # 提出済みのチェック（黄）
TOTAL_POINTS = "L2"    # 配点の合計（白、100でなければ赤）

# 出席・態度・テストそれぞれ（自動・手入力・採用）の列。配点は採用の列の2行目に置く
PARTS = [("出席", "C", "D", "E"), ("態度", "F", "G", "H"), ("テスト", "I", "J", "K")]
ADOPTED_COLS = [5, 8, 11]  # 成績表が読む列（1始まり）: 採用値3つ。前後に学籍番号(1)と合計(12)


@dataclass
class Cells:
    values: list[list]
    yellow: list[str] = field(default_factory=list)
    red: list[tuple[str, str]] = field(default_factory=list)  # (範囲, 条件付き書式の式)


@dataclass
class Book:
    tabs: dict[str, list[list]]
    yellow: dict[str, list[str]] = field(default_factory=dict)


def submission_cells(subject: str, teacher: str, student_ids: list[str]) -> Cells:
    """提出用の表: 配点・提出済み・学生ごとの自動／手入力／採用値と合計。"""
    last = FIRST_ROW + len(student_ids) - 1
    top = ["科目名", subject, "担当", teacher, "提出済み", False, None, None, None, None, None, "配点の合計"]
    points = ["配点", None, None, None, None, None, None, None, None, None, None, "=SUM(E2,H2,K2)"]
    for name, _, _, adopted in PARTS:
        col = ord(adopted) - ord("A")
        points[col - 1] = name
    head = ["学籍番号", "氏名"]
    for name, *_ in PARTS:
        head += [f"{name}（自動）", f"{name}（手入力）", f"{name}（採用）"]
    head.append("合計")
    rows = [top, points, head]
    for i, sid in enumerate(student_ids):
        r = FIRST_ROW + i
        row = [sid, None]
        for _, auto, manual, _ in PARTS:
            row += [None, None, f'=IF({manual}{r}="",{auto}{r},{manual}{r})']
        row.append(f'=IF(COUNT(E{r},H{r},K{r})=0,"",SUM(E{r},H{r},K{r}))')
        rows.append(row)

    submitted = "$" + SUBMITTED_CELL[0] + "$" + SUBMITTED_CELL[1:]
    yellow = [p[3] + "2" for p in PARTS] + [SUBMITTED_CELL] + [f"{p[2]}{FIRST_ROW}:{p[2]}{last}" for p in PARTS]
    red = [(TOTAL_POINTS, f"=${TOTAL_POINTS[0]}${TOTAL_POINTS[1:]}<>100")]
    for _, _, _, c in PARTS:
        cell = f"{c}{FIRST_ROW}"
        red.append((f"{c}{FIRST_ROW}:{c}{last}",
                    f'=OR(AND({submitted}=TRUE,{cell}=""),'
                    f'AND({cell}<>"",OR(NOT(ISNUMBER({cell})),{cell}<0,{cell}>{c}$2)))'))
    return Cells(rows, yellow, red)


def gradebook_cells(subjects: list[str], rows: int) -> Book:
    """成績表（最小）: 設定のつなぎ先一覧（黄）と、それを経由して提出用の表の採用値・提出済みを読む集計。"""
    links = [["つなぎ先一覧", None], ["提出用の表のアドレスを貼る。学校のアカウントへ移したら、ここだけ貼り直す", None],
             ["科目", "アドレス"]]
    links += [[s, None] for s in subjects]
    last = FIRST_ROW + rows - 1
    cols = ",".join(str(c) for c in [1, *ADOPTED_COLS, 12])
    summary = [["集計", None, None, None, None], ["提出済み", None, None, None, None],
               ["学籍番号", "出席", "態度", "テスト", "合計"]]
    for k, _ in enumerate(subjects):
        url = f"{LINKS_SHEET}!$B${FIRST_ROW + k}"
        summary[1][1] = f"=IMPORTRANGE({url},\"'{SUBMISSION_TAB}'!{SUBMITTED_CELL}\")"
        summary.append([f"=CHOOSECOLS(IMPORTRANGE({url},\"'{SUBMISSION_TAB}'!A{FIRST_ROW}:L{last}\"),{cols})",
                        None, None, None, None])
    return Book({LINKS_SHEET: links, "集計": summary},
                {LINKS_SHEET: [f"B{FIRST_ROW}:B{FIRST_ROW + len(subjects) - 1}" if len(subjects) > 1 else f"B{FIRST_ROW}"]})
