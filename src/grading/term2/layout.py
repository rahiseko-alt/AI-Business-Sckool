"""後期バージョンの Google スプレッドシートの中身（セルの値と式・黄色の範囲・赤の条件）を組み立てる。

ここは「何をどのセルに置くか」だけを決める。実際に Google ドライブへ書き込むのは別（コネクタ経由）。
色の決まり（ADR 0003）: 黄＝人が入力、白＝式（保護付き）、赤＝要確認。
成績表が提出用の表を読むときは、必ず「設定」シートのつなぎ先一覧のアドレスを経由する
（学校のアカウントへ移したとき、そこを貼り直すだけで済むように）。
提出用の表が成績表を読むときは、「出席の写し」の B1 にある成績表のアドレスだけを経由する。
"""

from dataclasses import dataclass, field

SUBMISSION_TAB = "提出"
LINKS_SHEET = "設定"
SUMMARY_SHEET = "集計"
ROSTER_SHEET = "名簿"                  # 成績表: 学籍番号・氏名・カタカナ・学科（黄）
SUBJECT_SHEET = "科目"                 # 成績表: 学科・科目名・担当・単位・形態（黄）
EXCLUDE_SHEET = "受講しない学生"        # 成績表: 学籍番号・科目名（黄）
FIRST_ROW = 4          # 学生の行の開始（1行目＝科目名・担当・提出済み・学科、2行目＝配点、3行目＝見出し）
SUBMITTED_CELL = "F1"  # 提出済みのチェック（黄）
DEPT_CELL = "H1"       # 提出用の表の学科（白）
TOTAL_POINTS = "L2"    # 配点の合計（白、100でなければ赤）
INTAKE_SHEET = "出席の受け口"          # 成績表: 学籍番号×科目ごとの授業数・欠席・遅刻
CHECK_SHEET = "確認"                   # 成績表: 未提出・要確認の件数と一覧（赤が0件なら印刷してよい）
GRADES = ["A", "B", "C", "D", "E"]     # 評定（設定の E4:E8）。E は 0 点以上
GRADE_MIN = "F4:F7"                    # 設定: A〜D の「この点以上」（黄）。上から大きい順
LINK_SHEET_ATTENDANCE = "出席簿つなぎ"  # 成績表: 出席簿を読む唯一の場所。出席簿の形が変わったらここだけ直す
ATTENDANCE_COPY = "出席の写し"          # 提出用の表: 成績表の受け口の写し（B1 に成績表のアドレス）
ROSTER_COPY = "名簿の写し"              # 提出用の表: 成績表の名簿と受講しない学生の写し
LAST_ROW = 1000                        # 写しや一覧を数える範囲の下端
SLOTS = 35                             # 提出用の表の学生の行数（学科の人数＋入れ替わりの余り）
EXCLUDE_ROWS = 50                      # 受講しない学生の黄の行数
ROSTER_LAST = 203                      # 名簿の写しの下端（名簿200人まで）

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


def _abs(cell: str) -> str:
    return f"${cell[0]}${cell[1:]}"


def submission_cells(subject: str, teacher: str, dept: str, slots: int = SLOTS) -> Cells:
    """提出用の表: 配点・提出済み・学生ごとの自動／手入力／採用値と合計。

    学生の行は、名簿の写しから自分の学科の学生を名簿の順に並べる（k 行目＝学科の k 人目）。
    受講しない学生はその行が空欄になる（詰めない。詰めると、先生が手入力した点が別の学生の行へずれるため）。"""
    last = FIRST_ROW + slots - 1
    dept_ref = f"{SUBMISSION_TAB}!{_abs(DEPT_CELL)}"
    top = ["科目名", subject, "担当", teacher, "提出済み", False, "学科", dept, None, None, None, "配点の合計"]
    points = ["配点", None, None, None, None, None, None, None, None, None, None, "=SUM(E2,H2,K2)"]
    for name, _, _, adopted in PARTS:
        points[ord(adopted) - ord("A") - 1] = name
    head = ["学籍番号", "氏名"]
    for name, *_ in PARTS:
        head += [f"{name}（自動）", f"{name}（手入力）", f"{name}（採用）"]
    head += ["合計", "授業数", "欠席", "遅刻"]
    rows = [top, points, head]
    rc = lambda c: f"'{ROSTER_COPY}'!${c}${FIRST_ROW}:${c}${ROSTER_LAST}"
    for i in range(slots):
        r = FIRST_ROW + i
        sid = f"IFERROR(INDEX({rc('A')},MATCH(ROW()-{FIRST_ROW - 1},{rc('E')},0)),\"\")"   # 行によらず同じ式
        sid_cell = (f'=IF({sid}="","",IF(COUNTIFS({rc("G")},{sid},{rc("H")},$B$1)>0,"",{sid}))')
        name = f'=IF($A{r}="","",IFERROR(INDEX({rc("B")},MATCH($A{r},{rc("A")},0)),""))'
        row = [sid_cell, name]
        for _, auto, manual, _ in PARTS:
            row += [None, None, f'=IF($A{r}="","",IF({manual}{r}="",{auto}{r},{manual}{r}))']
        row[2] = _auto_attendance(r)
        row.append(f'=IF(COUNT(E{r},H{r},K{r})=0,"",SUM(E{r},H{r},K{r}))')
        row += [_from_copy(col, r) for col in "IJK"]
        rows.append(row)

    submitted = _abs(SUBMITTED_CELL)
    yellow = [p[3] + "2" for p in PARTS] + [SUBMITTED_CELL] + [f"{p[2]}{FIRST_ROW}:{p[2]}{last}" for p in PARTS]
    red = [(TOTAL_POINTS, f"={_abs(TOTAL_POINTS)}<>100"),
           (f"C{FIRST_ROW}:C{last}", f'=C{FIRST_ROW}="要確認"'),
           # 条件付き書式は別シートを直接指せないので INDIRECT を使う
           (f"A{FIRST_ROW}:A{last}",
            f'=AND($A{FIRST_ROW}<>"",COUNTIF(INDIRECT("{rc("A")}"),$A{FIRST_ROW})=0)')]
    for _, _, manual, c in PARTS:
        cell = f"{c}{FIRST_ROW}"
        red.append((f"{c}{FIRST_ROW}:{c}{last}",
                    f'=AND($A{FIRST_ROW}<>"",OR(AND({submitted}=TRUE,{cell}=""),'
                    f'AND({cell}<>"",OR(NOT(ISNUMBER({cell})),{cell}<0,{cell}>{c}$2))))'))
        # 学生がいない行に手入力が残っている（名簿や受講しない学生を直した後のずれ）
        red.append((f"{manual}{FIRST_ROW}:{manual}{last}", f'=AND($A{FIRST_ROW}="",{manual}{FIRST_ROW}<>"")'))
    copy = [["成績表のアドレス", None], ["成績表の「出席の受け口」の写し。ここは直さない", None], _INTAKE_HEAD,
            [f"=IMPORTRANGE(B1,\"'{INTAKE_SHEET}'!A{FIRST_ROW}:K{LAST_ROW}\")"]]
    gb = f"'{ATTENDANCE_COPY}'!$B$1"
    roster = [["成績表の「名簿」と「受講しない学生」の写し。ここは直さない"] + [None] * 7, [None] * 8,
              ["学籍番号", "氏名", "カタカナ", "学科", "学科内の順番", None, "受講しない学籍番号", "科目名"]]
    for i in range(ROSTER_LAST - FIRST_ROW + 1):
        r = FIRST_ROW + i
        row = [None] * 8
        if i == 0:
            row[0] = f"=IMPORTRANGE({gb},\"'{ROSTER_SHEET}'!A{FIRST_ROW}:D{ROSTER_LAST}\")"
            row[6] = f"=IMPORTRANGE({gb},\"'{EXCLUDE_SHEET}'!A{FIRST_ROW}:B{ROSTER_LAST}\")"
        row[4] = f'=IF(AND($A{r}<>"",$D{r}={dept_ref}),COUNTIFS($D${FIRST_ROW}:$D{r},{dept_ref},$A${FIRST_ROW}:$A{r},"<>"),"")'
        roster.append(row)
    return Cells(rows, yellow, red, {ATTENDANCE_COPY: copy, ROSTER_COPY: roster})


_INTAKE_HEAD = ["学籍番号", "科目", "授業数（つなぎ）", "欠席（つなぎ）", "遅刻（つなぎ）",
                "授業数（手入力）", "欠席（手入力）", "遅刻（手入力）", "授業数", "欠席", "遅刻"]


def _from_copy(col: str, r: int) -> str:
    """出席の写しから、この学生・この科目（B1）の採用値を取る。行が無ければ空欄。"""
    rng = lambda c: f"'{ATTENDANCE_COPY}'!${c}${FIRST_ROW}:${c}${LAST_ROW}"
    key = f'{rng("A")},$A{r},{rng("B")},$B$1'
    return f'=IF($A{r}="","",IF(COUNTIFS({key})=0,"",SUMIFS({rng(col)},{key})))'


def _auto_attendance(r: int) -> str:
    """前期の決まり: 出席率＝1−（欠席＋遅刻÷3）÷授業数。60%未満は0点、4%下がるごとに配点の1割を減点。
    整数のまま比べる（3×授業数を分母にする）ので、割り切れない出席率でも境目がずれない。"""
    n, a, late = f"M{r}", f"N{r}", f"O{r}"
    bad = f"OR(NOT(ISNUMBER({n})),{n}<=0,NOT(ISNUMBER({a})),NOT(ISNUMBER({late})),{a}<0,{late}<0,{a}+{late}/3>{n})"
    lost, whole = f"(3*{a}+{late})", f"(3*{n})"
    return (f'=IF(OR($A{r}="",$E$2=""),"",IF({bad},"要確認",IF(5*({whole}-{lost})<3*{whole},0,'
            f'$E$2-$E$2/10*INT(100*{lost}/(4*{whole})))))')


def master_cells(roster: list[tuple[str, str, str, str]], subjects: list[tuple[str, str, str, int, str]]) -> Book:
    """成績表の名簿・科目・受講しない学生（すべて黄）。roster: (学籍番号, 氏名, カタカナ, 学科)。
    subjects: (学科, 科目名, 担当, 単位, 形態)。"""
    names = [[ROSTER_SHEET, None, None, None], ["入れ替わりがあれば、ここだけ直す", None, None, None],
             ["学籍番号", "氏名", "カタカナ", "学科"]] + [list(r) for r in roster]
    subs = [[SUBJECT_SHEET] + [None] * 4, [None] * 5, ["学科", "科目名", "担当", "単位", "形態"]] + [list(s) for s in subjects]
    excl = [[EXCLUDE_SHEET, None], ["受けない学生だけ1行ずつ書く。書くとその科目の提出用の表から消える", None],
            ["学籍番号", "科目名"]]
    last = lambda n: FIRST_ROW + n - 1
    return Book({ROSTER_SHEET: names, SUBJECT_SHEET: subs, EXCLUDE_SHEET: excl},
                {ROSTER_SHEET: [f"A{FIRST_ROW}:D{last(len(roster))}"],
                 SUBJECT_SHEET: [f"A{FIRST_ROW}:E{last(len(subjects))}"],
                 EXCLUDE_SHEET: [f"A{FIRST_ROW}:B{last(EXCLUDE_ROWS)}"]})


def _grade_ok(prefix: str = f"{LINKS_SHEET}!") -> str:
    """評定の基準（設定の F4:F7）が4つとも数で、上から大きい順、D の下限が0より大きいか。"""
    f = lambda r: f"{prefix}$F${r}"
    return (f"AND(COUNT({prefix}$F$4:$F$7)=4,{f(4)}>{f(5)},{f(5)}>{f(6)},{f(6)}>{f(7)},{f(7)}>0)")


def _grade(r: int) -> str:
    """合計から評定を出す（前期の決まり: 下限の降順に見て、合計がその点以上なら決まる。どれも満たさなければ E）。
    基準が未入力・順番がおかしいとき、出席・態度・テストのどれかが数でないとき（空欄・要確認）は「要確認」
    （前期も、値がそろわない学生の評定は推測で決めず止めていた）。"""
    f = lambda k: f"{LINKS_SHEET}!$F${k}"
    nested = '"E"'
    for k, g in reversed(list(enumerate(GRADES[:-1], FIRST_ROW))):
        nested = f'IF($F{r}>={f(k)},"{g}",{nested})'
    return (f'=IF(OR($B{r}="",$F{r}=""),"",IF(OR(NOT({_grade_ok()}),COUNT($C{r},$D{r},$E{r})<3),"要確認",'
            f'{nested}))')


def _summary_check(r: int, head: str) -> str:
    """集計の確認内容: 何がおかしいかを「・」でつないで並べる。何も無ければ空欄。"""
    bad = lambda c: (f'AND(${c}{r}<>"",${c}{r}<>"要確認",OR(NOT(ISNUMBER(${c}{r})),${c}{r}<0,'
                     f'${c}{r}>INDEX(${c}:${c},{head})))')
    return (f'=IF($A{r}="","",TEXTJOIN("・",TRUE,IF($B{r}="","学生のいない行に手入力",""),'
            f'IF(AND($B{r}<>"",$G{r}=TRUE,OR($C{r}="",$D{r}="",$E{r}="")),"提出済みなのに空欄",""),'
            f'IF(OR({bad("C")},{bad("D")},{bad("E")}),"点数がおかしい（配点超え・負・数値でない）",""),'
            f'IF($C{r}="要確認","出席の数がおかしい","")))')


def _intake_check(r: int) -> str:
    """出席の受け口の確認内容。学生のいない行への手入力と、採用値（授業数・欠席・遅刻）のおかしさ。"""
    i, j, k = f"$I{r}", f"$J{r}", f"$K{r}"
    bad = f"OR(NOT(ISNUMBER({i})),{i}<=0,NOT(ISNUMBER({j})),NOT(ISNUMBER({k})),{j}<0,{k}<0,{j}+{k}/3>{i})"
    return (f'=IF(AND($A{r}="",COUNTA($F{r}:$H{r})=0),"",IF($A{r}="","学生のいない行に手入力",'
            f'IF({bad},"授業数・欠席・遅刻がおかしい","")))')


def _check_sheet(last_sum: int, last_intake: int, height: int) -> tuple[list[list], list[tuple[str, str]]]:
    """確認シート: 未提出の科目と、集計・出席の受け口の確認内容を一覧にする。赤が0件になったら印刷してよい。"""
    sm = lambda c: f"{SUMMARY_SHEET}!${c}${FIRST_ROW}:${c}${last_sum}"
    ik = lambda c: f"'{INTAKE_SHEET}'!${c}${FIRST_ROW}:${c}${last_intake}"
    block_head = f"MOD(ROW({sm('A')})-{FIRST_ROW},{height})=0"   # 科目ごとの見出しの行
    ok = _grade_ok()
    rows = [[CHECK_SHEET] + [None] * 8, ["赤が0件になったら印刷してよい"] + [None] * 8,
            ["未提出", f"=SUMPRODUCT(({block_head})*({sm('G')}<>TRUE))",
             "要確認", f'=COUNTIF({sm("I")},"?*")+COUNTIF({ik("L")},"?*")+IF({ok},0,1)',
             "評定の基準", f'=IF({ok},"","未入力または順番がおかしい")', None, None, None],
            [None] * 9,
            ["未提出の科目", None, "学籍番号", "科目", "何がおかしいか（成績）", None,
             "学籍番号", "科目", "何がおかしいか（出席）"],
            [f'=IFERROR(FILTER({sm("A")},{block_head},{sm("G")}<>TRUE),"")', None,
             f'=IFERROR(FILTER({{{sm("B")},{sm("A")},{sm("I")}}},{sm("I")}<>""),"")', None, None, None,
             f'=IFERROR(FILTER({{{ik("A")},{ik("B")},{ik("L")}}},{ik("L")}<>""),"")', None, None]]
    red = [("B3", "=$B$3>0"), ("D3", "=$D$3>0"), ("F3", '=$F$3<>""'), (f"A6:A{LAST_ROW}", '=A6<>""'),
           (f"C6:E{LAST_ROW}", '=$E6<>""'), (f"G6:I{LAST_ROW}", '=$I6<>""')]
    return rows, red


def gradebook_cells(subjects: list[tuple[str, str]], slots: int = SLOTS) -> Book:
    """成績表: 設定のつなぎ先一覧と評定の基準（黄）、それを経由して提出用の表を読む集計・出席の受け口、確認。

    subjects: (学科, 科目名)。科目シートと同じ順に並べる。
    集計は科目ごとのまとまりで、各行に 科目名・学籍番号・出席・態度・テスト・合計・提出済み・評定・確認内容、
    その右に提出用の表の手入力（出席・態度・テスト）。"""
    links = [["つなぎ先一覧", None, None], ["提出用の表のアドレスを貼る。学校のアカウントへ移したら、ここだけ貼り直す", None, None],
             ["科目", "アドレス", "学科"]]
    links += [[s, None, d] for d, s in subjects] + [["出席簿", None, None]]
    # 右の E:F に評定の基準（A〜D の下限は黄、E は 0 で固定）
    links = [row + [None] * 3 for row in links]
    links += [[None] * 6 for _ in range(FIRST_ROW + len(GRADES) - 1 - len(links))]
    links[FIRST_ROW - 2][4:6] = ["評定", "この点以上"]
    for k, g in enumerate(GRADES):
        links[FIRST_ROW - 1 + k][4] = g
    links[FIRST_ROW - 1 + len(GRADES) - 1][5] = 0
    book_url = f"{LINKS_SHEET}!$B${FIRST_ROW + len(subjects)}"
    last = FIRST_ROW + slots - 1
    cols = ",".join(str(c) for c in [1, *ADOPTED_COLS, 12])
    summary = [[SUMMARY_SHEET] + [None] * 11, [None] * 12,
               ["科目", "学籍番号", "出席", "態度", "テスト", "合計", "提出済み", "評定", "確認内容",
                "出席（手入力）", "態度（手入力）", "テスト（手入力）"]]
    # 科目ごとのまとまり（見出し1行＋学生 slots 行）。何番目のまとまりかを行番号から出し、
    # 設定のつなぎ先一覧の同じ番目を読む。どのまとまりも同じ式なので、1つ書いて下へ写せる
    height = slots + 1
    nth = f"INT((ROW()-{FIRST_ROW})/{height})+1"
    head = f"{FIRST_ROW}+{height}*({nth}-1)"     # このまとまりの見出しの行（配点・提出済みがある）
    col = lambda c: f"{LINKS_SHEET}!${c}${FIRST_ROW}:${c}${FIRST_ROW + len(subjects) - 1}"
    url = f"INDEX({col('B')},{nth})"
    imp = lambda rng: f"IMPORTRANGE({url},\"'{SUBMISSION_TAB}'!{rng}\")"
    manual_cols = ",".join(str(ord(p[2]) - ord("A") + 1) for p in PARTS)   # 提出用の表の手入力の列
    points_cols = ",".join(str(c - 4) for c in [*ADOPTED_COLS, 12])         # E2:L2 のうち配点3つと合計
    for k in range(len(subjects)):
        head_row = FIRST_ROW + k * height
        summary.append([f'=INDEX({col("C")},{nth})&"　"&INDEX({col("A")},{nth})', None,
                        f"=CHOOSECOLS({imp('E2:L2')},{points_cols})", None, None, None,
                        f"={imp(SUBMITTED_CELL)}", None,
                        f'=IF($F{head_row}<>100,"配点の合計が100でない","")', None, None, None])
        for i in range(slots):
            r = head_row + 1 + i
            first = i == 0
            summary.append([f'=IF(AND($B{r}="",COUNTA($J{r}:$L{r})=0),"",INDEX({col("A")},{nth}))',
                            f"=CHOOSECOLS({imp(f'A{FIRST_ROW}:L{last}')},{cols})" if first else None,
                            None, None, None, None,
                            f'=IF($B{r}="","",INDEX($G:$G,{head}))', _grade(r), _summary_check(r, head),
                            f"=CHOOSECOLS({imp(f'A{FIRST_ROW}:L{last}')},{manual_cols})" if first else None,
                            None, None])
    link = [["出席簿つなぎ", None], ["出席簿の形が変わったら、ここの式だけ直す（学籍番号・科目・授業数・欠席・遅刻の順に並べる）", None],
            ["学籍番号", "科目", "授業数", "欠席", "遅刻"],
            [f"=IMPORTRANGE({book_url},\"'出席'!A2:E{LAST_ROW}\")"]]
    # 受け口の行は 科目（科目シートの順）× 学科の学生（名簿の順）。科目ごとに slots 行ずつ取る。
    # 名簿や科目を直せば、ここも自動で並び直る（式は行によらず同じなので、1行書いて下へ写せる）
    n_rows = len(subjects) * slots
    intake = [["出席の受け口", None], ["出席簿つなぎから入る。間に合わないときは黄の欄に手で打つ（手入力が優先）", None],
              _INTAKE_HEAD + ["確認内容"]]
    lk = lambda c: f"'{LINK_SHEET_ATTENDANCE}'!${c}${FIRST_ROW}:${c}${LAST_ROW}"
    block = f"INT((ROW()-{FIRST_ROW})/{slots})+1"
    nth = f"MOD(ROW()-{FIRST_ROW},{slots})+1"
    ros = lambda c: f"{ROSTER_SHEET}!${c}${FIRST_ROW}:${c}${ROSTER_LAST}"
    sub = lambda c: f"{SUBJECT_SHEET}!${c}${FIRST_ROW}:${c}${FIRST_ROW + 96}"
    for k in range(n_rows):
        r = FIRST_ROW + k
        sid = f'=IFERROR(INDEX(FILTER({ros("A")},{ros("D")}=INDEX({sub("A")},{block})),{nth}),"")'
        subject = f'=IF($A{r}="","",INDEX({sub("B")},{block}))'
        key = f"{lk('A')},$A{r},{lk('B')},$B{r}"
        linked = [f'=IF($A{r}="","",IF(COUNTIFS({key})=0,"",SUMIFS({lk(c)},{key})))' for c in "CDE"]
        adopted = [f'=IF($A{r}="","",IF({m}{r}="",{c}{r},{m}{r}))' for c, m in zip("CDE", "FGH")]
        intake.append([sid, subject, *linked, None, None, None, *adopted, _intake_check(r)])
    last_pair = FIRST_ROW + max(n_rows, 1) - 1
    i = f"$I{FIRST_ROW}"
    intake_red = [(f"I{FIRST_ROW}:K{last_pair}",
                   f'=AND($A{FIRST_ROW}<>"",OR(NOT(ISNUMBER({i})),{i}<=0,NOT(ISNUMBER($J{FIRST_ROW})),$J{FIRST_ROW}>{i},'
                   f'$J{FIRST_ROW}+$K{FIRST_ROW}/3>{i}))'),
                  (f"F{FIRST_ROW}:H{last_pair}", f'=AND($A{FIRST_ROW}="",F{FIRST_ROW}<>"")')]
    link_rows = FIRST_ROW + len(subjects)
    check, check_red = _check_sheet(FIRST_ROW - 1 + len(subjects) * height, last_pair, height)
    return Book({LINKS_SHEET: links, SUMMARY_SHEET: summary, LINK_SHEET_ATTENDANCE: link, INTAKE_SHEET: intake,
                 CHECK_SHEET: check},
                {LINKS_SHEET: [f"B{FIRST_ROW}:B{link_rows}", GRADE_MIN],
                 INTAKE_SHEET: [f"F{FIRST_ROW}:H{last_pair}"]},
                {INTAKE_SHEET: intake_red, LINKS_SHEET: [(GRADE_MIN, f"=NOT({_grade_ok('')})")],
                 CHECK_SHEET: check_red})
