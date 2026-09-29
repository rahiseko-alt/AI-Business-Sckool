"""リテラシー最終課題の番号版を作る。

使い方: python3 make_version.py 07          -> kit-07.txt / responses-07.csv / key-07.md
        python3 make_version.py 01 40       -> 01〜40 をまとめて作る
SALT（環境変数 LIT_SALT）は毎年変え、教員だけが持つ。SALT が同じなら同じ番号は同じ版になる。
学生に配るのは kit-NN.txt と responses-NN.csv だけ。key-NN.md は教員だけが持つ。
"""
import csv
import datetime as dt
import os
import random
import sys

SALT = os.environ.get("LIT_SALT", "demo-2026")
WD = "月火水木金土日"
OUT = os.environ.get("LIT_OUT", os.path.dirname(os.path.abspath(__file__)))

SEI = ["アオキ", "イシダ", "ウエノ", "エンドウ", "オオタ", "カトウ", "キムラ", "クボ", "コバヤシ", "サイトウ",
       "シミズ", "スギタ", "セキ", "タカギ", "チバ", "ツジ", "ナカノ", "ニシダ", "ノムラ", "ハヤシ",
       "ヒラノ", "フジタ", "ホンダ", "マツダ", "ミヤケ", "ムラタ", "モリ", "ヤノ", "ヨシダ", "ワダ"]
MEI = ["アオイ", "イツキ", "ウタ", "エマ", "カイ", "キョウ", "サク", "シオン", "スズ", "ソラ",
       "タクミ", "チヒロ", "ツバサ", "ナギ", "ヒナタ", "フウカ", "ホノカ", "マオ", "ミナト", "メイ",
       "ユイ", "ヨウ", "リク", "ルカ", "レン"]


def wd(d):
    return WD[d.weekday()]


def jd(d):
    return f"{d.month}月{d.day}日"


def ts(t):
    # Google フォームの書き出しと同じ形（時は0埋めしない）
    return f"{t.year}/{t.month:02d}/{t.day:02d} {t.hour}:{t.minute:02d}:{t.second:02d}"


def build(no):
    r = random.Random(f"{SALT}-{no}")
    # --- 日程と定員 ---
    firsts = [dt.date(2026, 12, d) for d in range(1, 12) if dt.date(2026, 12, d).weekday() < 5]
    d1 = r.choice(firsts)
    d2 = d1 + dt.timedelta(days=7)
    deadline = dt.datetime.combine(d1 - dt.timedelta(days=12), dt.time(17, 0))
    revised = deadline.date() - dt.timedelta(days=r.randint(4, 7))
    optchange = dt.date(2026, 10, 25)
    start = dt.datetime(2026, 10, 19, 9, 0)
    c1 = r.randint(10, 13)
    k1 = r.randint(2, 4)
    n1 = c1 + k1
    n2 = r.randint(9, 12)
    c2old = n2 - r.randint(1, 2)
    c2 = c2old + 4
    unit = r.choice([8, 10, 12, 15])

    # --- 人（全員架空）---
    names = r.sample([s + " " + m for s in SEI for m in MEI], n1 + n2 + 6)
    ids = r.sample(range(1000, 10000), n1 + n2 + 6)
    people = [{"name": names[i], "mail": f"s{ids[i]}@example.com"} for i in range(n1 + n2 + 6)]
    valid = people[:n1 + n2]
    for i, p in enumerate(valid):
        p["sess"] = 1 if i < n1 else 2
    cancels = people[n1 + n2:n1 + n2 + 2]
    lates = people[n1 + n2 + 2:n1 + n2 + 4]

    span = int((deadline - start).total_seconds())
    used = set()

    def rt(lo=0, hi=span - 3600):
        while True:
            s = r.randint(lo, hi)
            if s // 60 not in used:
                used.add(s // 60)
                return start + dt.timedelta(seconds=s)

    rows = []  # (time, mail, name, sess, consent, note, kind, handtyped)

    def add(t, mail, name, sess, note="", kind="", hand=False):
        rows.append({"t": t, "mail": mail, "name": name, "sess": sess,
                     "ok": r.choice(["はい", "はい", "いいえ"]), "note": note, "kind": kind, "hand": hand})

    for p in valid:
        add(rt(), p["mail"], p["name"], p["sess"])
    # 重複3人: 大文字の書き換え・手入力の空白。1人目は第2回→第1回に変更（最新は遅い時刻）
    d1s = [p for p in valid if p["sess"] == 1]
    d2s = [p for p in valid if p["sess"] == 2]
    dups = [r.choice(d1s[:-2]), r.choice(d2s), r.choice([p for p in d1s if p not in d1s[:1]])]
    dups = list(dict.fromkeys(id(x) for x in dups))
    dups = [p for p in valid if id(p) in dups]
    for j, p in enumerate(dups):
        last = [x for x in rows if x["mail"] == p["mail"]][0]
        # 最新の行を締切直前の時間帯へ、古い行を早い時間帯へ
        last["t"] = rt(span - 5 * 86400, span - 3600)
        first_t = rt(0, span // 3)
        old_sess = 2 if p["sess"] == 1 else 1
        if j == 0:
            last["mail"] = "S" + p["mail"][1:]  # 大文字
        elif j == 1:
            last["mail"] = p["mail"] + " "  # 後ろに空白（電話で受けた手入力）
            last["hand"] = True
            last["note"] = "電話受付"
        else:
            last["mail"] = p["mail"].replace("@example.com", "@EXAMPLE.COM")
        add(first_t, p["mail"], p["name"], old_sess)
    # 取消2人: 申込 → 後でキャンセル（1人は大文字で送信）
    for j, p in enumerate(cancels):
        s = r.choice([1, 2])
        t0 = rt(0, span // 2)
        add(t0, p["mail"], p["name"], s)
        m = p["mail"] if j == 0 else "S" + p["mail"][1:]
        add(rt(span // 2, span - 3600), m, p["name"], s, note=r.choice(["キャンセルします", "都合が悪くなったのでキャンセルでお願いします"]))
    # テスト送信2行
    add(rt(0, 3 * 3600), "unei01@example.com", "テスト", 1, note="送信テスト", kind="test")
    add(rt(0, 3 * 3600), "unei.check@example.com", "テスト 2", 2, note="動作確認", kind="test")
    # 締切後2行: 同じ日の17:02 と 翌日
    add(deadline + dt.timedelta(minutes=2, seconds=r.randint(1, 59)), lates[0]["mail"], lates[0]["name"], 1, kind="late")
    add(deadline + dt.timedelta(hours=17, minutes=r.randint(0, 50), seconds=r.randint(1, 59)),
        lates[1]["mail"], lates[1]["name"], 2, kind="late")
    # 電話受付の手入力（全角の「第１回」）をさらに2行
    early_hand = [x for x in rows if x["kind"] == "" and not x["hand"] and x["t"].date() >= optchange and "キャンセル" not in x["note"]]
    for x in r.sample(early_hand, 2):
        x["hand"] = True
        x["note"] = "電話受付"

    for x in rows:
        if x["hand"]:
            x["sesstxt"] = "第１回" if x["sess"] == 1 else "第２回"
        elif x["t"].date() < optchange:
            x["sesstxt"] = f"{x['sess']}回目"
        else:
            x["sesstxt"] = f"第{x['sess']}回"

    rows.sort(key=lambda x: x["name"])  # 前任者が氏名で並べ替えた
    return dict(no=no, d1=d1, d2=d2, deadline=deadline, revised=revised, optchange=optchange,
                c1=c1, c2old=c2old, c2=c2, unit=unit, rows=rows)


def answers(v):
    """ルールどおりの正解。verify.py が別の書き方で同じ値になるかを確かめる。"""
    rows = v["rows"]
    test = [x for x in rows if x["mail"].strip().lower().startswith("unei")]
    late = [x for x in rows if x not in test and x["t"] > v["deadline"]]
    ok = [x for x in rows if x not in test and x not in late]
    latest = {}
    for x in sorted(ok, key=lambda x: x["t"]):
        latest[x["mail"].strip().lower()] = x
    persons = [x for x in latest.values() if "キャンセル" not in x["note"]]
    persons.sort(key=lambda x: x["t"])
    s1 = [x for x in persons if x["sess"] == 1]
    s2 = [x for x in persons if x["sess"] == 2]
    b4, b5 = min(len(s1), v["c1"]), min(len(s2), v["c2"])
    waits = s1[v["c1"]:] + s2[v["c2"]:]
    return dict(B1=len(test), B2=len(late), B3=len(persons), B4=b4, B5=b5, B6=len(waits),
                B7=s1[v["c1"]]["mail"].strip().lower(), B8=v["unit"] * (b4 + b5 + 5))


def naive(v):
    """AIに丸投げしたときに出やすい値（罠が効いているかの確認用）。"""
    rows = v["rows"]
    notest = [x for x in rows if not x["mail"].startswith("unei")]
    dateonly = [x for x in notest if x["t"].date() <= v["deadline"].date()]
    exact = {}
    for x in sorted([x for x in notest if x["t"] <= v["deadline"]], key=lambda x: x["t"]):
        exact[x["mail"]] = x
    b3_case = len([x for x in exact.values() if "キャンセル" not in x["note"]])
    first = {}
    for x in [x for x in notest if x["t"] <= v["deadline"]]:  # 行の順（氏名順）で最初の回答を採用
        first.setdefault(x["mail"].strip().lower(), x)
    s1_roworder = [x for x in first.values() if "キャンセル" not in x["note"] and x["sesstxt"] in ("第1回", "1回目")]
    a = answers(v)
    n2 = a["B5"]
    return dict(B2_dateonly=len(notest) - len(dateonly), B3_casesensitive=b3_case,
                B5_oldcap=min(n2, v["c2old"]), B7_roworder=(s1_roworder[v["c1"]]["mail"].strip().lower() if len(s1_roworder) > v["c1"] else "なし"),
                draft_valid=len(notest), draft_rows=len(rows))


def ok_traps(v):
    a, n = answers(v), naive(v)
    return (n["B2_dateonly"] != a["B2"] and n["B3_casesensitive"] != a["B3"] and n["B5_oldcap"] != a["B5"]
            and n["B7_roworder"] != a["B7"] and n["draft_valid"] != a["B3"] and a["B4"] == v["c1"] and a["B5"] <= v["c2"])


def make(no):
    tries = 0
    while True:
        v = build(f"{no}-{tries}" if tries else no)
        if ok_traps(v):
            break
        tries += 1
    v["no"] = no
    a, n = answers(v), naive(v)
    d1, d2 = v["d1"], v["d2"]
    wrongwd = WD[(d2.weekday() + 1) % 7]
    dl = v["deadline"]

    with open(os.path.join(OUT, f"responses-{no}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["タイムスタンプ", "メールアドレス", "氏名（カナ）", "希望回", "録画に映ってよい", "備考"])
        for x in v["rows"]:
            w.writerow([ts(x["t"]), x["mail"], x["name"], x["sesstxt"], x["ok"], x["note"]])

    draft = [
        "件名：【参加確定】スマホ時短術ミニ講座のご案内",
        "参加確定のみなさま",
        "この度はお申し込みいただき、誠にありがとうございます！",
        f"第1回は{jd(d1)}（{wd(d1)}）、第2回は{jd(d2)}（{wrongwd}）です。",
        "時間はどちらも16:20〜17:30、会場はB棟3階の301教室です。",
        f"有効なお申し込みは{n['draft_valid']}名で、第1回は定員に達したため、一部の方は補欠となりました。",
        "補欠の方には、空きが出た順に個別にメールでご連絡します。",
        "キャンセルは各回の前日までに、申込フォームから同じメールアドレスで、備考に「キャンセル」と書いて送信してください。",
        "当日の資料は「リンクを知っている全員が編集可」で共有します。",
        "講座は録画し、参加者全員が映った動画をYouTubeで一般公開します。",
        "当日は受付番号でご案内しますので、このメールを受付でお見せください。",
        "送信方法：参加確定者全員のアドレスを「宛先（To）」に入れて一斉送信する。",
        f"印刷：1部{v['unit']}円 × {n['draft_rows']}部（フォームの回答数）＝{v['unit'] * n['draft_rows']}円。",
        "チラシ：ネットで見つけたイラストをそのまま使った。",
        "名簿：申込者の氏名とメールアドレスの一覧を、教室のドアに貼っておく。",
        "申込データ：講座終了後1か月で削除する。",
    ]
    kit = f"""ビジネス情報リテラシー 最終課題　材料 {no}番（この番号以外の材料で出したものは採点しません）

■ 課題
あなたは学内の「スマホ時短術ミニ講座」の運用担当を、前任者から今日引き継ぎました。
渡されたもの: (1) 運用ルール（この紙の下） (2) 申込フォームの回答 responses-{no}.csv (3) 前任者が作ったお知らせメールの下書きと運用メモ
制限時間は40分。AIは使ってかまいません。ただし正しいかどうかは、この紙の運用ルールだけで決まります。

■ 手順
1. 開始の合図と同時にスマホの画面録画を始める。提出が終わるまで止めない（通知はおやすみモードで切る）
2. responses-{no}.csv を自分の Google スプレッドシートに取り込み、ファイル名を「最終課題_{no}_自分の氏名」にする
3. シート「入力」のA1に、教員が黒板に書く「開始の合言葉」を入れる（録画に映るように）
4. シート「結果」に次の8つを出す（B列に値だけ。単位や「名」は付けない）
   B1 運営のテスト送信の行数
   B2 締切後に届いた行数（テスト送信は除く）
   B3 有効な申込者の人数（テスト送信・締切後・取消を除いた人数）
   B4 第1回の参加確定の人数
   B5 第2回の参加確定の人数
   B6 補欠の人数（第1回と第2回の合計）
   B7 第1回の補欠1番の人のメールアドレス（小文字、前後の空白なし）
   B8 資料の印刷費（円）
5. シート「訂正」に、下書きとメモ（行01〜16）の誤りだけを書く。1行に1か所: A列＝行番号、B列＝正しい内容
   誤りとは「運用ルール・申込データ・カレンダーと食い違う所」だけ。言い回しや敬語の好みは誤りではない（書くと減点）
6. Google ドキュメントに、行01〜11を正しく直した「送れる状態のメール本文」を作る。誤り以外の文は1字も変えない
7. スプレッドシートとドキュメントを、教員のアカウントだけに「閲覧者」で共有する
8. 画面録画を止めて Google ドライブに上げ、提出フォームに「シートURL・ドキュメントURL・録画URL」を入れて送信する
   送信の時刻が開始から40分を過ぎると、1分ごとに合計点から1点引かれます（0点が下限）

■ 運用ルール（これが正しさの基準）
R1 講座: 第1回 {jd(d1)}（{wd(d1)}）、第2回 {jd(d2)}（{wd(d2)}）。どちらも16:20〜17:30、B棟3階301教室
R2 定員: 第1回 {v['c1']}名、第2回 {v['c2old']}名
R3 申込締切: {jd(dl.date())}（{wd(dl.date())}）17:00。17:00より後に届いた回答は無効
R4 同じ人かどうかはメールアドレスで決める。大文字・小文字と前後の空白は区別しない。同じ人の回答が複数あるときは、いちばん新しい回答だけを有効にする
R5 いちばん新しい回答の備考に「キャンセル」とある人は、申込取消
R6 メールアドレスが「unei」で始まる回答は運営のテスト送信。数えない
R7 参加確定は回ごとの先着順（有効な回答のタイムスタンプが早い順）。定員を超えた人は補欠。補欠には空きが出た順に個別にメールで連絡する
R8 キャンセルは各回の2日前の17:00まで。申込フォームから同じメールアドレスで、備考に「キャンセル」と書いて送信する
R9 参加者へのメールは、全員のアドレスを「BCC」に入れて送る
R10 資料は、参加確定者のメールアドレスを指定して「閲覧者」で共有する。「リンクを知っている全員」にはしない
R11 講座は録画する。録画に映すのは「録画に映ってよい」に「はい」と答えた人だけ。YouTubeの「限定公開」で上げ、URLは参加確定者にだけ知らせる
R12 チラシ・資料の画像は、自分で撮影・作成したもの（自分で生成したAI画像を含む）だけを使う
R13 受付は受付番号で行う。申込者の氏名・メールアドレスの一覧は掲示も配布もしない
R14 資料の印刷は1部{v['unit']}円。部数は参加確定者の合計＋予備5部
R15 申込データは講座終了後1か月で削除する
改定（{jd(v['revised'])}）: 椅子を追加したため、R2 の第2回の定員を{v['c2']}名に変更する
補足: {jd(v['optchange'])}より前は、希望回の選択肢が「1回目」「2回目」だった。備考が「電話受付」の行は、前任者が電話で受けて手で入力した

■ 前任者のお知らせメール下書き（行01〜11）と運用メモ（行12〜16）
""" + "\n".join(f"{i + 1:02d} {s}" for i, s in enumerate(draft)) + "\n"
    with open(os.path.join(OUT, f"kit-{no}.txt"), "w", encoding="utf-8") as f:
        f.write(kit)

    fixed = list(draft)
    fixed[3] = f"第1回は{jd(d1)}（{wd(d1)}）、第2回は{jd(d2)}（{wd(d2)}）です。"
    fixed[5] = f"有効なお申し込みは{a['B3']}名で、第1回は定員に達したため、一部の方は補欠となりました。"
    fixed[7] = "キャンセルは各回の2日前の17:00までに、申込フォームから同じメールアドレスで、備考に「キャンセル」と書いて送信してください。"
    fixed[8] = "当日の資料は、参加確定者のメールアドレスを指定して「閲覧者」で共有します。"
    fixed[9] = "講座は録画し、「録画に映ってよい」に「はい」と答えた方だけが映った動画を、YouTubeの限定公開で参加確定者にだけお知らせします。"
    errs = [
        ("04", "E2 曜日", f"第2回は{jd(d2)}（{wd(d2)}）", "R1・カレンダー"),
        ("06", "E1 人数", f"{a['B3']}名（下書きの{n['draft_valid']}名は重複・取消・締切後を数えた値）", "B3"),
        ("08", "E6 キャンセル期限", "各回の2日前の17:00まで", "R8"),
        ("09", "E4 資料の共有", "参加確定者を指定して「閲覧者」で共有", "R10"),
        ("10", "E5 録画", "同意した人だけ映す・限定公開・確定者にだけURL", "R11"),
        ("12", "E3 送信方法", "BCCに入れて送る", "R9"),
        ("13", "E8 印刷費", f"{v['unit']}円×{a['B4'] + a['B5'] + 5}部＝{a['B8']}円", "R14・B4・B5"),
        ("14", "E7 画像", "自分で撮影・作成した画像（自分で生成したAI画像を含む）に差し替える", "R12"),
        ("15", "E9 名簿の掲示", "掲示しない（受付番号で受付）", "R13"),
    ]
    key = f"""# 正解表 {no}番（教員だけが持つ。SALT={SALT}）

## 結果シート
| セル | 正解 | 罠に落ちたときの値 |
| --- | --- | --- |
| B1 | {a['B1']} | |
| B2 | {a['B2']} | 日付だけで比べる: {n['B2_dateonly']}（{ts(dl + dt.timedelta(minutes=2))[:-3]}台の行を見逃す） |
| B3 | {a['B3']} | 大文字・空白を区別: {n['B3_casesensitive']}／下書きの値: {n['draft_valid']} |
| B4 | {a['B4']} | |
| B5 | {a['B5']} | 改定前の定員{v['c2old']}を使う: {n['B5_oldcap']} |
| B6 | {a['B6']} | |
| B7 | {a['B7']} | 行の順（氏名順）で数える: {n['B7_roworder']} |
| B8 | {a['B8']} | 下書きの値: {v['unit'] * n['draft_rows']} |

## 訂正シート（仕込んだ誤り9か所。これ以外の行を書いたら誤検出）
| 行 | 誤り | 正しい内容（この要点が入っていれば○） | 根拠 |
| --- | --- | --- | --- |
""" + "\n".join(f"| {e[0]} | {e[1]} | {e[2]} | {e[3]} |" for e in errs) + """

誤りでない行（直したら誤検出）: 01 02 03 05 07 11 16。03の「！」、05の16:20、07・11・16はルールどおり。

## 直したメール本文（行04・06・08・09・10 だけが変わる。ほかは1字も変えない）
""" + "\n".join(f"{i + 1:02d} {s}" for i, s in enumerate(fixed[:11])) + "\n"
    with open(os.path.join(OUT, f"key-{no}.md"), "w", encoding="utf-8") as f:
        f.write(key)
    return v, a, n


if __name__ == "__main__":
    lo = int(sys.argv[1])
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else lo
    for i in range(lo, hi + 1):
        v, a, n = make(f"{i:02d}")
        print(v["no"], a, n)
