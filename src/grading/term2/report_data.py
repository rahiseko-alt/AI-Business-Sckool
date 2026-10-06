"""成績表の「通知表データ」「例外」「特記事項」シートの中身（セルの値と式・黄色の範囲・赤の条件）を組み立てる。

通知表データは 1人1行。通知表_印刷用はここだけを読む（人は直さない、白）。
前期の欄は前期成績の写しから、後期の欄は集計から、評定の例外は例外シートから、文は特記事項シートから取る。
どの欄の式も、行番号（と後期の科目のまとまりの中の位置）を除けば同じなので、1つ書いて右と下へ写せる。
色の決まりは layout と同じ（黄＝人が入力、白＝式、赤＝要確認）。
"""

from grading.term2.first_term import SHEET as FIRST_TERM_SHEET
from grading.term2.layout import (CHECK_SHEET, EXCEPTION_ROWS, EXCEPTION_SHEET, FIRST_ROW, INTAKE_SHEET,
                                  REMARKS_ROWS, REMARKS_SHEET, ROSTER_LAST, ROSTER_SHEET, SLOTS, SUBJECT_LAST,
                                  SUBJECT_SHEET, SUMMARY_SHEET, Book)

REPORT_SHEET = "通知表データ"
FIELDS = ["科目", "形態", "点数", "評定", "設定", "取得"]   # 科目1つぶんの欄（この順に6列）
CARD_SLOTS = 13           # 通知表の科目の欄の数（前期・後期それぞれ）
FIRST_COL = 5             # 前期1つめの科目の列（E）
STUDENTS = 60             # 通知表データの行数
FIRST_TERM_LINES = 720    # 前期成績の科目ごとの行数（60人×12科目）
SUBJECTS = 24             # 後期の科目数（集計・出席の受け口の下端を決める）
TOTALS = ["前期設定計", "前期取得計", "後期設定計", "後期取得計", "年間設定計", "年間取得計",
          "前期授業時数", "前期出席時数", "後期授業時数", "後期出席時数", "年間授業時数", "年間出席時数",
          "前期出席率", "後期出席率", "年間出席率", "不合格", "要確認", "特記事項"]


def _col(n: int) -> str:
    """列番号（1始まり）から列の文字（A, B, …, Z, AA, …）。"""
    s = ""
    while n:
        n, k = divmod(n - 1, 26)
        s = chr(ord("A") + k) + s
    return s


def _rng(sheet: str, c: str, last: int) -> str:
    return f"{sheet}!${c}${FIRST_ROW}:${c}${last}"


def _ex(c: str) -> str:
    return _rng(EXCEPTION_SHEET, c, FIRST_ROW + EXCEPTION_ROWS - 1)


def _summary_last(subjects: int, slots: int) -> int:
    """集計の下端（科目ごとに 見出し1行＋学生 slots 行）。gradebook_cells と同じ数え方。"""
    return FIRST_ROW - 1 + subjects * (slots + 1)


def _slot_head(term: str, first: int) -> str:
    """見出し「前期3_評定」など。列の位置から何番目の科目のどの欄かを出すので、どの列でも同じ式。"""
    fields = ",".join(f'"{f}"' for f in FIELDS)
    return (f'="{term}"&(INT((COLUMN()-{first})/{len(FIELDS)})+1)&"_"&'
            f'CHOOSE(MOD(COLUMN()-{first},{len(FIELDS)})+1,{fields})')


def _second_term_slot(r: int, base: int, last_sum: int) -> list[str]:
    """後期の科目1つぶん（科目・形態・点数・評定・設定・取得）。base はこのまとまりの1列目。
    例外シートに書かれた科目は、点数を空欄・評定を指定の文字・取得を空欄にする（点数そのものは書き換えない）。"""
    w = len(FIELDS)
    first = FIRST_COL + CARD_SLOTS * w
    at = lambda k: f"{_col(base + k)}{r}"
    name, grade, credits = at(0), at(3), at(4)
    sm = lambda c: _rng(SUMMARY_SHEET, c, last_sum)
    sub = lambda c: _rng(SUBJECT_SHEET, c, SUBJECT_LAST)
    nth = f"INT((COLUMN()-{first})/{w})+1"           # 何番目の科目か（集計でのこの学生の何行目か）
    pick = lambda c: f'IFERROR(INDEX(FILTER({sm(c)},{sm("B")}=$A{r}),{nth}),"")'
    from_subject = lambda c: (f'=IF({name}="","",IFERROR(INDEX(FILTER({sub(c)},{sub("A")}=$D{r},'
                              f'{sub("B")}={name}),1),""))')
    ex = f"COUNTIFS({_ex('A')},$A{r},{_ex('B')},{name})>0"   # この学生のこの科目に例外がある
    ex_grade = f'IFERROR(INDEX(FILTER({_ex("C")},{_ex("A")}=$A{r},{_ex("B")}={name}),1),"")'
    return [f'=IF($A{r}="","",{pick("A")})',
            from_subject("E"),
            f'=IF({name}="","",IF({ex},"",{pick("F")}))',
            f'=IF({name}="","",IF({ex},{ex_grade},{pick("H")}))',
            from_subject("D"),
            # 評定が E・F・要確認、または例外のときは取得しない
            f'=IF(OR({name}="",{grade}="",{grade}="E",{grade}="F",{grade}="要確認",{ex}),"",{credits})']


def report_data_cells(subjects: int = SUBJECTS, slots: int = SLOTS, students: int = STUDENTS,
                      first_term_lines: int = FIRST_TERM_LINES) -> Book:
    """通知表データ: 1行目に題、3行目に見出し、4行目から学生 students 人ぶん。
    列は 学籍番号・氏名・カタカナ・学科、前期の科目 CARD_SLOTS 個×6欄、後期の科目 CARD_SLOTS 個×6欄、計と出席と判定。

    subjects・slots は集計と出席の受け口の大きさ（gradebook_cells と同じ数）。"""
    w = len(FIELDS)
    second = FIRST_COL + CARD_SLOTS * w         # 後期1つめの科目の列（CE）
    tail = second + CARD_SLOTS * w              # 計の列の始まり（FE）
    last_sum = _summary_last(subjects, slots)
    last_intake = FIRST_ROW - 1 + max(subjects * slots, 1)
    last_first = FIRST_ROW - 1 + first_term_lines
    last_card = FIRST_ROW - 1 + students        # 前期成績の学生ごとの計も同じ人数
    width = tail + len(TOTALS) - 1
    ros = lambda c: _rng(ROSTER_SHEET, c, ROSTER_LAST)
    ft = lambda c, last: _rng(FIRST_TERM_SHEET, c, last)
    ik = lambda c: _rng(f"'{INTAKE_SHEET}'", c, last_intake)
    rm = lambda c: _rng(REMARKS_SHEET, c, FIRST_ROW + REMARKS_ROWS - 1)

    title = ["通知表データ（通知表_印刷用が読む。1人1行。直さない）"] + [None] * (width - 1)
    head = (["学籍番号", "氏名", "カタカナ", "学科"] + [_slot_head("前期", FIRST_COL)] * (CARD_SLOTS * w)
            + [_slot_head("後期", second)] * (CARD_SLOTS * w) + TOTALS)
    rows = [title, [None] * width, head]
    for i in range(students):
        r = FIRST_ROW + i
        at = lambda n: f"{_col(n)}{r}"
        t = lambda k: at(tail + k)              # 計の k 番目の欄（0＝前期設定計）
        row = [f'=IFERROR(INDEX({ros("A")},ROW()-{FIRST_ROW - 1}),"")']
        row += [f'=IF($A{r}="","",INDEX({ros(c)},ROW()-{FIRST_ROW - 1}))' for c in "BCD"]
        # 前期: 前期成績の写しのうちこの学生の行を、列の位置で「何番目の科目の何の欄」かを選んで取る
        lines = f"{FIRST_TERM_SHEET}!$D${FIRST_ROW}:$I${last_first}"   # 科目・形態・点数・評定・設定・取得
        row += [f'=IF($A{r}="","",IFERROR(INDEX(FILTER({lines},{ft("A", last_first)}=$A{r}),'
                f'INT((COLUMN()-{FIRST_COL})/{w})+1,MOD(COLUMN()-{FIRST_COL},{w})+1),""))'] * (CARD_SLOTS * w)
        for k in range(CARD_SLOTS):
            row += _second_term_slot(r, second + k * w, last_sum)
        first_total = lambda c: (f'=IF($A{r}="","",IFERROR(INDEX({ft(c, last_card)},'
                                 f'MATCH($A{r},{ft("K", last_card)},0)),""))')
        sum_of = lambda k: f'=IF($A{r}="","",SUM({",".join(at(second + j * w + k) for j in range(CARD_SLOTS))}))'
        attend = lambda c: f"SUMIFS({ik(c)},{ik('A')},$A{r})"
        row += [first_total("L"), first_total("M"), sum_of(4), sum_of(5),
                f'=IF($A{r}="","",N({t(0)})+{t(2)})', f'=IF($A{r}="","",N({t(1)})+{t(3)})',
                first_total("N"), first_total("O"),
                f'=IF($A{r}="","",{attend("I")})',
                # 出席時数＝授業時数−欠席−遅刻÷3（前期の決まり）
                f'=IF($A{r}="","",{t(8)}-{attend("J")}-{attend("K")}/3)',
                f'=IF($A{r}="","",N({t(6)})+N({t(8)}))', f'=IF($A{r}="","",N({t(7)})+N({t(9)}))',
                f'=IF(N({t(6)})=0,"",{t(7)}/{t(6)})', f'=IF(N({t(8)})=0,"",{t(9)}/{t(8)})',
                f'=IF(N({t(10)})=0,"",{t(11)}/{t(10)})',
                # 不合格: 前期・後期どちらかに E・F がある、または例外が1つでもある
                f'=IF($A{r}="","",OR(COUNTIF($E{r}:${_col(tail - 1)}{r},"E")+COUNTIF($E{r}:${_col(tail - 1)}{r},"F")>0,'
                f'COUNTIF({_ex("A")},$A{r})>0))',
                # 要確認: 後期に要確認がある、または確認シートに未提出・要確認が残っている
                f'=IF($A{r}="","",OR(COUNTIF(${_col(second)}{r}:${_col(tail - 1)}{r},"要確認")>0,'
                f'{CHECK_SHEET}!$B$3>0,{CHECK_SHEET}!$D$3>0))',
                f'=IF($A{r}="","",IFERROR(INDEX(FILTER({rm("B")},{rm("A")}=$A{r}),1),"該当なし"))']
        rows.append(row)
    return Book({REPORT_SHEET: rows})


def exception_cells(subjects: int = SUBJECTS, slots: int = SLOTS) -> Book:
    """例外: 1行書くと、その科目が通知表で黒塗り・点数と取得が空欄・評定が指定の文字になる。
    E列（白）は書いた行の確認内容。学籍番号と科目の組が集計に無い、または表示する評定が無いと赤。"""
    last = FIRST_ROW + EXCEPTION_ROWS - 1
    sm = lambda c: _rng(SUMMARY_SHEET, c, _summary_last(subjects, slots))
    rows = [[EXCEPTION_SHEET] + [None] * 4,
            ["1行書くと、その科目が通知表で黒塗り・点数と取得が空欄・評定が指定の文字になる。点数そのものは書き換えない"]
            + [None] * 4,
            ["学籍番号", "科目", "表示する評定", "理由", "確認"]]
    for i in range(EXCEPTION_ROWS):
        r = FIRST_ROW + i
        rows.append([None] * 4 + [f'=IF(AND($A{r}="",$B{r}=""),"",IF(COUNTIFS({sm("B")},$A{r},{sm("A")},$B{r})=0,'
                                  f'"学籍番号または科目が見つからない",IF($C{r}="","表示する評定が無い","")))'])
    return Book({EXCEPTION_SHEET: rows}, {EXCEPTION_SHEET: [f"A{FIRST_ROW}:D{last}"]},
                {EXCEPTION_SHEET: [(f"E{FIRST_ROW}:E{last}", f'=$E{FIRST_ROW}<>""')]})


def remarks_cells() -> Book:
    """特記事項: 書いた学生だけ、その文が通知表に出る（書かなければ「該当なし」）。
    C列（白）は書いた行の確認内容。学籍番号が名簿に無い、または文が無いと赤。"""
    last = FIRST_ROW + REMARKS_ROWS - 1
    ros = _rng(ROSTER_SHEET, "A", ROSTER_LAST)
    rows = [[REMARKS_SHEET, None, None], ["書いた学生だけ、その文が通知表に出る。書かなければ「該当なし」", None, None],
            ["学籍番号", "文", "確認"]]
    for i in range(REMARKS_ROWS):
        r = FIRST_ROW + i
        rows.append([None, None, f'=IF(AND($A{r}="",$B{r}=""),"",IF(COUNTIF({ros},$A{r})=0,"学籍番号が名簿に無い",'
                                 f'IF($B{r}="","文が無い","")))'])
    return Book({REMARKS_SHEET: rows}, {REMARKS_SHEET: [f"A{FIRST_ROW}:B{last}"]},
                {REMARKS_SHEET: [(f"C{FIRST_ROW}:C{last}", f'=$C{FIRST_ROW}<>""')]})
