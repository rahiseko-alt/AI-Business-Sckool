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
INTAKE_SHEET = "出席の受け口"          # 成績表: 学籍番号×科目ごとの授業数・欠席・遅刻
LINK_SHEET_ATTENDANCE = "出席簿つなぎ"  # 成績表: 出席簿を読む唯一の場所。出席簿の形が変わったらここだけ直す
ATTENDANCE_COPY = "出席の写し"          # 提出用の表: 成績表の受け口の写し
LAST_ROW = 1000                        # 写しや一覧を数える範囲の下端

# 出席・態度・テストそれぞれ（自動・手入力・採用）の列。配点は採用の列の2行目に置く
PARTS = [("出席", "C", "D", "E"), ("態度", "F", "G", "H"), ("テスト", "I", "J", "K")]
ADOPTED_COLS = [5, 8, 11]  # 成績表が読む列（1始まり）: 採用値3つ。前後に学籍番号(1)と合計(12)


@dataclass
class Cells:
    values: list[list]
    yellow: list[str] = field(default_factory=list)
    red: list[tuple[str, str]] = field(default_factory=list)  # (範囲, 条件付き書式の式)
    extra_tabs: dict[str, list[list]] = field(default_factory=dict)


@dataclass
class Book:
    tabs: dict[str, list[list]]
    yellow: dict[str, list[str]] = field(default_factory=dict)
    red: dict[str, list[tuple[str, str]]] = field(default_factory=dict)


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
    head += ["合計", "授業数", "欠席", "遅刻"]
    rows = [top, points, head]
    for i, sid in enumerate(student_ids):
        r = FIRST_ROW + i
        row = [sid, None]
        for _, auto, manual, _ in PARTS:
            row += [None, None, f'=IF({manual}{r}="",{auto}{r},{manual}{r})']
        row[2] = _auto_attendance(r)
        row.append(f'=IF(COUNT(E{r},H{r},K{r})=0,"",SUM(E{r},H{r},K{r}))')
        row += [_from_copy(col, r) for col in "IJK"]
        rows.append(row)

    submitted = "$" + SUBMITTED_CELL[0] + "$" + SUBMITTED_CELL[1:]
    yellow = [p[3] + "2" for p in PARTS] + [SUBMITTED_CELL] + [f"{p[2]}{FIRST_ROW}:{p[2]}{last}" for p in PARTS]
    red = [(TOTAL_POINTS, f"=${TOTAL_POINTS[0]}${TOTAL_POINTS[1:]}<>100"),
           (f"C{FIRST_ROW}:C{last}", f'=C{FIRST_ROW}="要確認"')]
    for _, _, _, c in PARTS:
        cell = f"{c}{FIRST_ROW}"
        red.append((f"{c}{FIRST_ROW}:{c}{last}",
                    f'=OR(AND({submitted}=TRUE,{cell}=""),'
                    f'AND({cell}<>"",OR(NOT(ISNUMBER({cell})),{cell}<0,{cell}>{c}$2)))'))
    copy = [["成績表のアドレス", None], ["成績表の「出席の受け口」の写し。ここは直さない", None], _INTAKE_HEAD,
            [f"=IMPORTRANGE(B1,\"'{INTAKE_SHEET}'!A{FIRST_ROW}:K{LAST_ROW}\")"]]
    return Cells(rows, yellow, red, {ATTENDANCE_COPY: copy})


_INTAKE_HEAD = ["学籍番号", "科目", "授業数（つなぎ）", "欠席（つなぎ）", "遅刻（つなぎ）",
                "授業数（手入力）", "欠席（手入力）", "遅刻（手入力）", "授業数", "欠席", "遅刻"]


def _from_copy(col: str, r: int) -> str:
    """出席の写しから、この学生・この科目（B1）の採用値を取る。行が無ければ空欄。"""
    rng = lambda c: f"'{ATTENDANCE_COPY}'!${c}${FIRST_ROW}:${c}${LAST_ROW}"
    key = f'{rng("A")},$A{r},{rng("B")},$B$1'
    return f'=IF(COUNTIFS({key})=0,"",SUMIFS({rng(col)},{key}))'


def _auto_attendance(r: int) -> str:
    """前期の決まり: 出席率＝1−（欠席＋遅刻÷3）÷授業数。60%未満は0点、4%下がるごとに配点の1割を減点。
    整数のまま比べる（3×授業数を分母にする）ので、割り切れない出席率でも境目がずれない。"""
    n, a, late = f"M{r}", f"N{r}", f"O{r}"
    bad = f"OR(NOT(ISNUMBER({n})),{n}<=0,NOT(ISNUMBER({a})),NOT(ISNUMBER({late})),{a}<0,{late}<0,{a}+{late}/3>{n})"
    lost, whole = f"(3*{a}+{late})", f"(3*{n})"
    return (f'=IF($E$2="","",IF({bad},"要確認",IF(5*({whole}-{lost})<3*{whole},0,'
            f'$E$2-$E$2/10*INT(100*{lost}/(4*{whole})))))')


def gradebook_cells(subjects: list[str], rows: int, student_ids: list[str] | None = None) -> Book:
    """成績表（最小）: 設定のつなぎ先一覧（黄）と、それを経由して提出用の表の採用値・提出済みを読む集計。"""
    links = [["つなぎ先一覧", None], ["提出用の表のアドレスを貼る。学校のアカウントへ移したら、ここだけ貼り直す", None],
             ["科目", "アドレス"]]
    links += [[s, None] for s in subjects] + [["出席簿", None]]
    book_url = f"{LINKS_SHEET}!$B${FIRST_ROW + len(subjects)}"
    last = FIRST_ROW + rows - 1
    cols = ",".join(str(c) for c in [1, *ADOPTED_COLS, 12])
    summary = [["集計", None, None, None, None], ["提出済み", None, None, None, None],
               ["学籍番号", "出席", "態度", "テスト", "合計"]]
    for k, _ in enumerate(subjects):
        url = f"{LINKS_SHEET}!$B${FIRST_ROW + k}"
        summary[1][1] = f"=IMPORTRANGE({url},\"'{SUBMISSION_TAB}'!{SUBMITTED_CELL}\")"
        summary.append([f"=CHOOSECOLS(IMPORTRANGE({url},\"'{SUBMISSION_TAB}'!A{FIRST_ROW}:L{last}\"),{cols})",
                        None, None, None, None])
    link = [["出席簿つなぎ", None], ["出席簿の形が変わったら、ここの式だけ直す（学籍番号・科目・授業数・欠席・遅刻の順に並べる）", None],
            ["学籍番号", "科目", "授業数", "欠席", "遅刻"],
            [f"=IMPORTRANGE({book_url},\"'出席'!A2:E{LAST_ROW}\")"]]
    pairs = [(sid, s) for s in subjects for sid in (student_ids or [])]
    intake = [["出席の受け口", None], ["出席簿つなぎから入る。間に合わないときは黄の欄に手で打つ（手入力が優先）", None], _INTAKE_HEAD]
    lk = lambda c: f"'{LINK_SHEET_ATTENDANCE}'!${c}${FIRST_ROW}:${c}${LAST_ROW}"
    for k, (sid, subject) in enumerate(pairs):
        r = FIRST_ROW + k
        key = f"{lk('A')},$A{r},{lk('B')},$B{r}"
        linked = [f'=IF(COUNTIFS({key})=0,"",SUMIFS({lk(c)},{key}))' for c in "CDE"]
        adopted = [f'=IF({m}{r}="",{c}{r},{m}{r})' for c, m in zip("CDE", "FGH")]
        intake.append([sid, subject, *linked, None, None, None, *adopted])
    last_pair = FIRST_ROW + max(len(pairs), 1) - 1
    i = f"$I{FIRST_ROW}"
    intake_red = [(f"I{FIRST_ROW}:K{last_pair}",
                   f'=OR(NOT(ISNUMBER({i})),{i}<=0,NOT(ISNUMBER($J{FIRST_ROW})),$J{FIRST_ROW}>{i},'
                   f'$J{FIRST_ROW}+$K{FIRST_ROW}/3>{i})')]
    link_rows = FIRST_ROW + len(subjects)
    return Book({LINKS_SHEET: links, "集計": summary, LINK_SHEET_ATTENDANCE: link, INTAKE_SHEET: intake},
                {LINKS_SHEET: [f"B{FIRST_ROW}:B{link_rows}"],
                 INTAKE_SHEET: [f"F{FIRST_ROW}:H{last_pair}"]},
                {INTAKE_SHEET: intake_red})
