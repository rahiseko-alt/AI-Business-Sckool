"""成果物4「補欠のお知らせを出す」の番号版を作る。

使い方: LIT_SALT=秘密の語 python3 make.py 07      -> kit-07.txt / responses-07.csv / key-07.md
        LIT_SALT=秘密の語 python3 make.py 1 40
補欠役のアドレス（教員のテスト用アカウント）は環境変数 ROLE_HOKETSU で入れる。
学生に配るのは kit と CSV（教員がスプレッドシートにして本人だけに閲覧者で共有）。key は教員だけ。
"""
import csv
import datetime as dt
import os
import random
import sys

SALT = os.environ.get("LIT_SALT", "demo-2026")
OUT = os.environ.get("LIT_OUT", os.path.dirname(os.path.abspath(__file__)))
HOKETSU = os.environ.get("ROLE_HOKETSU", "hoketsu.yaku@example.com")
WD = "月火水木金土日"
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
    return f"{t.year}/{t.month:02d}/{t.day:02d} {t.hour}:{t.minute:02d}:{t.second:02d}"


def build(seed, fixed=None):
    r = random.Random(f"{SALT}-d4-{seed}")
    d1 = r.choice([dt.date(2026, 11, d) for d in range(16, 28) if dt.date(2026, 11, d).weekday() < 5])
    c1 = r.randint(8, 11)
    c2 = r.randint(10, 12)
    if fixed:  # 翌週データ（段11）: 日程・定員は本番と同じにする
        d1, c1, c2 = fixed["d1"], fixed["c1"], fixed["c2"]
    d2 = d1 + dt.timedelta(days=7)
    deadline = dt.datetime.combine(d1 - dt.timedelta(days=9), dt.time(17, 0))
    start = deadline - dt.timedelta(days=14)
    n1 = c1 + r.randint(2, 3)
    n2 = c2 - r.randint(1, 3)
    names = r.sample([s + " " + m for s in SEI for m in MEI], n1 + n2 + 3)
    ids = r.sample(range(1000, 10000), n1 + n2 + 3)
    ppl = [dict(name=names[i], mail=f"s{ids[i]}@example.com", sess=1 if i < n1 else 2) for i in range(n1 + n2)]
    span = int((deadline - start).total_seconds())
    rows = []

    def add(t, mail, name, sess, note=""):
        rows.append(dict(t=t, mail=mail, name=name, sess=sess, note=note))

    def rt(lo, hi):
        return start + dt.timedelta(seconds=r.randint(int(lo * span), int(hi * span)))

    for p in ppl:
        add(rt(0.0, 0.85), p["mail"], p["name"], p["sess"])
    s1 = [p for p in ppl if p["sess"] == 1]
    # X: 第2回→第1回に変更。最新は締切の直前で、大文字のアドレス
    x = r.choice(s1)
    last = [row for row in rows if row["mail"] == x["mail"]][0]
    last["t"], last["mail"], last["note"] = rt(0.93, 0.99), "S" + x["mail"][1:], "第1回に変えたいです"
    add(rt(0.0, 0.2), x["mail"], x["name"], 2)
    # Y: 同じ第1回を、あとで末尾に空白つきで送り直し（最新の時刻が遅くなる）
    y = r.choice([p for p in s1 if p is not x])
    add(rt(0.86, 0.92), y["mail"] + " ", y["name"], 1, "電話受付")
    # 取消1人
    z = dict(name=names[n1 + n2], mail=f"s{ids[n1 + n2]}@example.com")
    zs = r.choice([1, 2])
    add(rt(0.05, 0.4), z["mail"], z["name"], zs)
    add(rt(0.5, 0.8), z["mail"], z["name"], zs, "キャンセルします")
    # テスト2行と締切後1行
    add(start + dt.timedelta(minutes=r.randint(3, 60)), "unei01@example.com", "テスト", 1, "送信テスト")
    add(start + dt.timedelta(minutes=r.randint(61, 180)), "unei.check@example.com", "テスト 2", 2, "動作確認")
    add(deadline + dt.timedelta(minutes=r.randint(2, 8), seconds=r.randint(1, 59)),
        f"s{ids[n1 + n2 + 1]}@example.com", names[n1 + n2 + 1], 1)
    rows.sort(key=lambda row: row["name"])  # 前任者が氏名で並べ替えた
    return dict(d1=d1, d2=d2, deadline=deadline, c1=c1, c2=c2, rows=rows)


def answers(v):
    rows = v["rows"]
    ok = [x for x in rows if not x["mail"].strip().lower().startswith("unei") and x["t"] <= v["deadline"]]
    latest = {}
    for x in sorted(ok, key=lambda x: x["t"]):
        latest[x["mail"].strip().lower()] = x
    persons = sorted([x for x in latest.values() if "キャンセル" not in x["note"]], key=lambda x: x["t"])
    s1 = [x for x in persons if x["sess"] == 1]
    s2 = [x for x in persons if x["sess"] == 2]
    return dict(B1=len(persons), B2=min(len(s1), v["c1"]), B3=min(len(s2), v["c2"]), B4=max(0, len(s1) - v["c1"]),
                B5=s1[v["c1"]]["mail"].strip().lower(), B6=s1[v["c1"] - 1]["mail"].strip().lower(), N1=len(s1),
                FIRST1=s1[0]["mail"].strip().lower())


def naive(v):
    rows = v["rows"]
    ok = [x for x in rows if not x["mail"].strip().lower().startswith("unei") and x["t"] <= v["deadline"]]
    latest = {}
    for x in sorted(ok, key=lambda x: x["t"]):
        latest[x["mail"].strip().lower()] = x
    live = {k for k, x in latest.items() if "キャンセル" not in x["note"]}
    # 行の順（氏名順）で、その人の最新の回の人を並べる
    seen, roworder = set(), []
    for x in rows:
        k = x["mail"].strip().lower()
        if k in live and k not in seen and latest[k]["sess"] == 1:
            seen.add(k)
            roworder.append(k)
    # その人の最初の回答の時刻で並べる
    first = {}
    for x in sorted(ok, key=lambda x: x["t"]):
        first.setdefault(x["mail"].strip().lower(), x["t"])
    firsttime = sorted([k for k in live if latest[k]["sess"] == 1], key=lambda k: first[k])
    c1 = v["c1"]
    return dict(B5_roworder=roworder[c1], B6_roworder=roworder[c1 - 1], B5_firsttime=firsttime[c1],
                B6_firsttime=firsttime[c1 - 1], draft_n1=len([x for x in rows if x["sess"] == 1]))


def ok_traps(v):
    a, n = answers(v), naive(v)
    return (n["B5_roworder"] != a["B5"] and n["B5_firsttime"] != a["B5"] and n["B6_firsttime"] != a["B6"]
            and n["B6_roworder"] != a["B6"] and n["draft_n1"] != a["N1"] and a["B4"] >= 2)


def hidden_block(v, a):
    """段5（隠し行を足す）・段10（元を1行変える）・段11（翌週データ3本）の正解。"""
    dl = v["deadline"]
    first = [x for x in v["rows"] if x["mail"].strip().lower() == a["FIRST1"]][0]  # 第1回の先着1番の人
    extra = [dict(t=dl - dt.timedelta(days=3, minutes=17), mail="s0101@example.com", name="オオノ ハル", sess=2, note=""),
             dict(t=dl + dt.timedelta(minutes=1, seconds=10), mail="s0102@example.com", name="オオノ ナツ", sess=1, note=""),
             dict(t=dl - dt.timedelta(minutes=25), mail=" " + first["mail"].strip().upper(), name=first["name"], sess=1, note="念のためもう一度送ります")]
    v5 = dict(v, rows=v["rows"] + extra)
    a5 = answers(v5)
    conf = [x for x in sorted(v["rows"], key=lambda x: x["t"]) if x["sess"] == 1 and x["mail"].strip().lower() == a["B6"]][-1]
    rows10 = [dict(x, note="キャンセルします") if x is conf else x for x in v["rows"]]
    a10 = answers(dict(v, rows=rows10))
    def fmt(extra_rows):
        return "\n".join(f"  {ts(x['t'])},{x['mail']},{x['name']},第{x['sess']}回,{x['note']}" for x in extra_rows)
    out = f"""
## 段5 隠しテスト（シートのコピーのタブ「データ」の最後に3行を足す）
{fmt(extra)}
足したあとの正解: B1={a5['B1']} B2={a5['B2']} B3={a5['B3']} B4={a5['B4']} B5={a5['B5']} B6={a5['B6']}

## 段10 元を変える（シートのコピーで、{ts(conf['t'])} の {conf['mail']} の行の備考を「キャンセルします」に書き換える）
変えたあとの正解: B1={a10['B1']} B2={a10['B2']} B3={a10['B3']} B4={a10['B4']} B5={a10['B5']} B6={a10['B6']}

## 段11 翌週データ3本（hidden/week-NN-1〜3.csv を「データ」に貼り替える。日程・定員は同じ）
"""
    os.makedirs(os.path.join(OUT, "hidden"), exist_ok=True)
    for k in (1, 2, 3):
        while True:
            w = build(f"{v['no']}-week{k}", fixed=v)
            break
        aw = answers(w)
        with open(os.path.join(OUT, "hidden", f"week-{v['no']}-{k}.csv"), "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["タイムスタンプ", "メールアドレス", "氏名（カナ）", "希望回", "備考"])
            for x in w["rows"]:
                wr.writerow([ts(x["t"]), x["mail"], x["name"], f"第{x['sess']}回", x["note"]])
        out += f"- week-{v['no']}-{k}: B1={aw['B1']} B2={aw['B2']} B3={aw['B3']} B4={aw['B4']} B5={aw['B5']} B6={aw['B6']}\n"
    out += "\n（2026-09-29改訂）段は下から順に見て最初の✖で止める方式だったが、基礎＋独立採点に変更した（ADR 0001）。時間超過も「1分ごとに1段下げる」から「1分ごとに合計点（基礎を含む）から1点を引く（0点が下限）」に変えた\n"
    return out


def make(no):
    tries = 0
    while True:
        v = build(f"{no}-{tries}" if tries else no)
        if ok_traps(v):
            break
        tries += 1
    v["no"] = no
    a, n = answers(v), naive(v)
    d1, d2, dl = v["d1"], v["d2"], v["deadline"]
    send = dl.date() + dt.timedelta(days=1)
    wrongwd = WD[(d1.weekday() + 1) % 7]
    with open(os.path.join(OUT, f"responses-{no}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["タイムスタンプ", "メールアドレス", "氏名（カナ）", "希望回", "備考"])
        for x in v["rows"]:
            w.writerow([ts(x["t"]), x["mail"], x["name"], f"第{x['sess']}回", x["note"]])
    draft = [
        "件名：【補欠のお知らせ】スマホ家計簿ミニ講座（第1回）",
        "補欠登録のみなさま",
        "このたびはお申し込みいただき、本当にありがとうございます！",
        f"第1回は{jd(d1)}（{wrongwd}）16:20〜17:30、C棟2階205教室で開きます。",
        f"第1回は定員{v['c1']}名に対して、有効なお申し込みが{n['draft_n1']}名ありました。",
        "補欠の順番は、お名前の五十音順です。",
        "空きが出た場合は、補欠の番号順に、各回の2日前の17:00までにメールでご連絡します。",
        "繰り上げのご連絡を受けた方は、連絡の翌日の12:00までに、次のフォームからご返信ください：〔返信フォームのURL〕",
        "ご返信がない場合は、次の補欠の方にご連絡します。",
        "当日の資料は「リンクを知っている全員」が閲覧できる形で共有します。",
        "送信方法：補欠の方全員のアドレスを「CC」に入れて送る。",
        f"送信日：{jd(send)}（{wd(send)}）に送る。",
        "返信の記録：返信フォームの回答は、運営用のスプレッドシートに自動で記録する。",
    ]
    kit = f"""ビジネス情報リテラシー 成果物4　材料 {no}番（この番号以外の材料で出したものは採点しません）

■ 仕事
あなたは「スマホ家計簿ミニ講座」の運営担当を前任者から引き継ぎました。申込は締め切られ、第1回は定員を超えました。
申込データから参加確定と補欠を決め、前任者が書きかけた「補欠のお知らせ」の誤りだけを直して、補欠の方に送れる状態にしてください。
制限時間は40分。AIは使ってかまいません。ただし正しいかどうかは、この紙の運用ルールと申込データだけで決まります。

■ 手順
1. 開始の合図と同時にスマホの画面録画を始める。提出が終わるまで止めない（通知はおやすみモードで切る）
2. 教員が共有したスプレッドシート「成果物4_{no}_申込」を開き、「コピーを作成」して、名前を「成果物4_{no}_自分の氏名」にする。申込はタブ「データ」に入っている
3. タブ「入力」のA1に、黒板の「開始の合言葉」を入れる（録画に映るように）
4. タブ「結果」に次の6つを、タブ「データ」を数える式で出す（値を打ち込まない。教員はデータを差し替えて確かめる）
   B1 有効な申込者の人数（テスト送信・締切後・取消を除き、同じ人は1人）
   B2 第1回の参加確定の人数　B3 第2回の参加確定の人数　B4 第1回の補欠の人数
   B5 第1回の補欠1番の人のメールアドレス（小文字、前後の空白なし）
   B6 第1回で最後に参加確定になった人のメールアドレス（小文字、前後の空白なし）
5. タブ「順番」に、第1回の有効な人を先着順に並べた表を式で作る（A列 順位、B列 アドレス、C列 いちばん新しい有効な回答の時刻、D列 確定／補欠）
6. タブ「訂正」に、下書きとメモ（行01〜13）の誤りだけを書く。1行に1か所: A列＝行番号、B列＝正しい内容
   誤りとは「運用ルール・申込データ・カレンダーと食い違う所」だけ。言い回しや敬語の好みは誤りではない（書くと減点）。〔 〕は誤りではなく、自分で埋める所
7. Google フォームで「成果物4_{no}_繰り上げ返信」を作る（メールアドレスを収集する。質問は「繰り上げになったら参加しますか」はい／いいえ の1問）。回答の記録先をスプレッドシート「成果物4_{no}_返信記録」にする
8. Gmail で、行01〜10を正しく直したメールを作る。件名は行01の「件名：」より後ろ、本文は行02〜10を1行ずつ（行番号は付けない）。〔返信フォームのURL〕は7のフォームのURLにする。誤り以外の文は1字も変えない
   宛先（To）は自分、BCCに補欠役 {HOKETSU}（練習のため、補欠の方全員の代わりに補欠役1人に送る）。CCは使わない
   「送信日時を設定」で、黒板に書いた日時に予約送信する
9. スプレッドシート2つを、教員のアカウントだけに「閲覧者」で共有する
10. 画面録画を止めて YouTube に「限定公開」で上げる。提出フォームに「シートURL・返信記録シートURL・動画URL」を入れて送信する
   送信の時刻が開始から40分を過ぎると、1分ごとに合計点（基礎を含む）から1点を引きます（0点が下限）

■ 運用ルール（これが正しさの基準）
R1 講座: 第1回 {jd(d1)}（{wd(d1)}）、第2回 {jd(d2)}（{wd(d2)}）。どちらも16:20〜17:30、C棟2階205教室
R2 定員: 第1回 {v['c1']}名、第2回 {v['c2']}名
R3 申込締切: {jd(dl.date())}（{wd(dl.date())}）17:00。17:00より後に届いた回答は無効
R4 同じ人かどうかはメールアドレスで決める。大文字・小文字と前後の空白は区別しない。同じ人の回答が複数あるときは、いちばん新しい回答だけを有効にする
R5 いちばん新しい回答の備考に「キャンセル」とある人は、申込取消
R6 メールアドレスが「unei」で始まる回答は運営のテスト送信。数えない
R7 参加確定は回ごとの先着順。順番は、その人のいちばん新しい有効な回答のタイムスタンプが早い順。定員を超えた人は補欠で、補欠の番号も同じ順につける
R8 空きが出たら、補欠の番号順に、各回の2日前の17:00までにメールで連絡する。連絡を受けた人は、連絡の翌日の12:00までに返信する。返信がなければ次の補欠に連絡する
R9 参加者・補欠へのメールは、全員のアドレスを「BCC」に入れて送る
R10 資料は、参加確定者のメールアドレスを指定して「閲覧者」で共有する。「リンクを知っている全員」にはしない
R11 補欠のお知らせは、締切の翌日に送る。補欠の返信は Google フォームで受け、回答は運営用のスプレッドシートに自動で記録する（手で書き写さない）

■ 前任者の「補欠のお知らせ」下書き（行01〜10）と運用メモ（行11〜13）
""" + "\n".join(f"{i + 1:02d} {s}" for i, s in enumerate(draft)) + "\n"
    with open(os.path.join(OUT, f"kit-{no}.txt"), "w", encoding="utf-8") as f:
        f.write(kit)
    fixed = list(draft)
    fixed[3] = f"第1回は{jd(d1)}（{wd(d1)}）16:20〜17:30、C棟2階205教室で開きます。"
    fixed[4] = f"第1回は定員{v['c1']}名に対して、有効なお申し込みが{a['N1']}名ありました。"
    fixed[5] = "補欠の順番は、お申し込みの受付順（いちばん新しい有効な回答の時刻の順）です。"
    fixed[9] = "当日の資料は、参加確定者のメールアドレスを指定して「閲覧者」で共有します。"
    key = f"""# 正解表 成果物4 {no}番（教員だけが持つ。SALT={SALT}）

## 結果シート
| セル | 正解 | 罠に落ちたときの値 |
| --- | --- | --- |
| B1 | {a['B1']} | |
| B2 | {a['B2']} | |
| B3 | {a['B3']} | |
| B4 | {a['B4']} | |
| B5 | {a['B5']} | 行の順（氏名順）: {n['B5_roworder']}／最初の回答の時刻で並べる: {n['B5_firsttime']} |
| B6 | {a['B6']} | 行の順（氏名順）: {n['B6_roworder']}／最初の回答の時刻で並べる: {n['B6_firsttime']} |

第1回の有効な申込: {a['N1']}名（下書きの{n['draft_n1']}名は、CSVで「第1回」の行を全部数えた値）

## 訂正シート（誤り5か所。これ以外の行を書いたら誤検出）
| 行 | 誤り | 正しい内容（この要点が入っていれば○） | 根拠 |
| --- | --- | --- | --- |
| 04 | 曜日 | {jd(d1)}（{wd(d1)}） | R1・カレンダー |
| 05 | 人数 | 有効なお申し込みは{a['N1']}名 | R3〜R6 |
| 06 | 補欠の順 | 受付順（最新の有効な回答の時刻順）。五十音順ではない | R7 |
| 10 | 資料の共有 | 参加確定者を指定して「閲覧者」で共有 | R10 |
| 11 | 送信方法 | BCCに入れて送る | R9 |

誤りでない行（直したら誤検出）: 01 02 03 07 08 09 12 13。03の「本当に」「！」、07の「2日前の17:00」、08の「翌日の12:00」、12の{jd(send)}（{wd(send)}）、13の自動記録はルールどおり。08の〔返信フォームのURL〕は埋めるだけで、訂正には書かない。

## 送るメール（行04・05・06・10 だけが変わる。ほかは1字も変えない）
- 件名: {fixed[0][3:]}
- 宛先: 学生本人／CC: なし／BCC: 補欠役 {HOKETSU}／黒板の日時に予約送信
- 本文（08の〔 〕は学生のフォームのURL）:
""" + "\n".join(f"  {s}" for s in fixed[1:10]) + "\n" + hidden_block(v, a)
    with open(os.path.join(OUT, f"key-{no}.md"), "w", encoding="utf-8") as f:
        f.write(key)
    return v, a, n


if __name__ == "__main__":
    lo = int(sys.argv[1])
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else lo
    for i in range(lo, hi + 1):
        v, a, n = make(f"{i:02d}")
        print(f"{i:02d}", a, n)
