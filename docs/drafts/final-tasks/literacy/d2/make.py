"""成果物2「運営会議を開いて、決めたことを動かす」（ペア）の番号版を作る。

使い方: LIT_SALT=秘密の語 python3 make.py 07 --date 2026-10-21 --start 10:40
        LIT_SALT=秘密の語 python3 make.py 1 15 --date 2026-10-21 --start 10:40   （ペア01〜15）
  --date  成果物2を行う授業の日（会議の日）  --start 授業の開始時刻
出力: card-NN.txt（ペアの2人に配る）、responses-NN-A.csv（Aだけ）、responses-NN-B.csv（Bだけ）、key-NN.md（教員だけ）
"""
import csv
import datetime as dt
import os
import random
import sys

SALT = os.environ.get("LIT_SALT", "demo-2026")
OUT = os.environ.get("LIT_OUT", os.path.dirname(os.path.abspath(__file__)))
WD = "月火水木金土日"
SEI = ["アオキ", "イシダ", "ウエノ", "エンドウ", "オオタ", "カトウ", "キムラ", "クボ", "コバヤシ", "サイトウ",
       "シミズ", "スギタ", "セキ", "タカギ", "チバ", "ツジ", "ナカノ", "ニシダ", "ノムラ", "ハヤシ"]
MEI = ["アオイ", "イツキ", "ウタ", "エマ", "カイ", "サク", "シオン", "スズ", "ソラ", "タクミ",
       "チヒロ", "ツバサ", "ナギ", "ヒナタ", "ホノカ", "マオ", "ミナト", "メイ", "ユイ", "リク"]
THEMES = ["差し入れの果物は、りんごよりオレンジのほうが素晴らしい",
          "講座を開くなら、朝の時間帯のほうが夜より素晴らしい",
          "説明の資料は、紙のほうが画面より素晴らしい",
          "休憩の飲み物は、お茶よりコーヒーのほうが素晴らしい",
          "受付の目印は、看板より声かけのほうが素晴らしい",
          "講座の記念品は、ステッカーよりしおりのほうが素晴らしい",
          "会場は、広い教室より小さい教室のほうが素晴らしい",
          "開始の合図は、ベルより拍手のほうが素晴らしい",
          "講座のあとの感想は、紙のアンケートよりフォームのほうが素晴らしい",
          "告知は、掲示板よりメールのほうが素晴らしい"]
SHAKE = ["土日に当たる期限は、次の月曜にしようよ",
         "Keep のチェックリスト、講師さんにも入れておこうか",
         "締切の数分後に来た人も、人数に入れてあげようよ",
         "議事録は「リンクを知っている全員」にしておけば楽だよ",
         "ToDo3の期限は、会議の翌日でいいよね"]
TIMES = [(9, 0), (12, 0), (13, 0), (17, 0), (18, 30)]


def wd(d):
    return WD[d.weekday()]


def jd(d):
    return f"{d.month}月{d.day}日"


def jdw(t):
    return f"{t.month}月{t.day}日（{wd(t.date() if isinstance(t, dt.datetime) else t)}）{t.hour}:{t.minute:02d}"


def ts(t):
    return f"{t.year}/{t.month:02d}/{t.day:02d} {t.hour}:{t.minute:02d}:{t.second:02d}"


def shift(t):
    """土日なら前の金曜日の同じ時刻にする。"""
    while t.weekday() >= 5:
        t -= dt.timedelta(days=1)
    return t


def todos(r, meet_day, course_day):
    while True:
        n1, n2, n3 = r.randint(5, 9), r.randint(2, 4), r.randint(2, 6)
        t1, t2, t3 = r.sample(TIMES, 3)
        raw = [dt.datetime.combine(course_day - dt.timedelta(days=n1), dt.time(*t1)),
               dt.datetime.combine(course_day - dt.timedelta(days=n2), dt.time(*t2)),
               dt.datetime.combine(meet_day + dt.timedelta(days=n3), dt.time(*t3))]
        if sum(x.weekday() >= 5 for x in raw) == 1 and all(x.date() > meet_day for x in raw):
            return [(n1, t1), (n2, t2), (n3, t3)], raw, [shift(x) for x in raw]


def session_data(r, label, deadline):
    names = r.sample([s + " " + m for s in SEI for m in MEI], 12)
    ids = r.sample(range(1000, 10000), 12)
    n = r.randint(7, 9)
    start = deadline - dt.timedelta(days=10)
    rows = []
    for i in range(n):
        t = start + dt.timedelta(seconds=r.randint(0, int((deadline - start).total_seconds()) - 7200))
        rows.append([t, f"s{ids[i]}@example.com", names[i], ""])
    # 大文字で2回目を送った人（同じ人）
    d = r.randrange(n)
    t = rows[d][0] + dt.timedelta(hours=r.randint(3, 30))
    t = min(t, deadline - dt.timedelta(minutes=r.randint(20, 90)))
    rows.append([t, rows[d][1].upper(), rows[d][2], "念のためもう一度送ります"])
    # テスト送信
    rows.append([start + dt.timedelta(minutes=r.randint(5, 50)), "unei.test@example.com", "テスト", "送信テスト"])
    # 締切の数分後
    rows.append([deadline + dt.timedelta(minutes=r.randint(1, 6), seconds=r.randint(1, 59)),
                 f"s{ids[n]}@example.com", names[n], ""])
    rows.sort(key=lambda x: x[0])
    return rows, n


def make(no, day, start):
    r = random.Random(f"{SALT}-d2-{no}")
    th = r.sample(THEMES, 2)
    sh = r.sample(SHAKE, 2)
    s = dt.datetime.combine(day, start)
    m1 = (s + dt.timedelta(minutes=15), s + dt.timedelta(minutes=30))
    m2 = (s + dt.timedelta(minutes=33), s + dt.timedelta(minutes=48))
    end = s + dt.timedelta(minutes=85)
    weekdays = [day + dt.timedelta(days=k) for k in range(10, 30) if (day + dt.timedelta(days=k)).weekday() < 5]
    c1 = r.choice(weekdays)
    c2 = c1 + dt.timedelta(days=7)
    out = {}
    for tag, cday, m in (("A", c1, m1), ("B", c2, m2)):
        deadline = dt.datetime.combine(cday - dt.timedelta(days=r.randint(5, 8)), dt.time(r.choice([12, 17])))
        if deadline.date() <= day:
            deadline = dt.datetime.combine(day + dt.timedelta(days=1), dt.time(17))
        rows, count = session_data(r, tag, deadline)
        rules, raw, ok = todos(r, day, cday)
        out[tag] = dict(cday=cday, m=m, deadline=deadline, rows=rows, count=count, rules=rules, raw=raw, ok=ok)
        with open(os.path.join(OUT, f"responses-{no}-{tag}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["タイムスタンプ", "メールアドレス", "氏名（カナ）", "備考"])
            for x in rows:
                w.writerow([ts(x[0]), x[1], x[2], x[3]])

    def block(tag, host, guest, theme, n):
        o = out[tag]
        (a1, b1), (a2, b2), (a3, b3) = o["rules"]
        return f"""■ 会議{n}（ホスト＝{host}、相手＝{guest}）
会議の名前: [成果物2-{no}] 会議{n}
時刻: {jdw(o['m'][0])}〜{o['m'][1].hour}:{o['m'][1].minute:02d}（授業中。この時刻でカレンダーに予定を作る）
{host}が担当する講座: スマホ地図ミニ講座 第{n}回　{jd(o['cday'])}　16:20〜17:30
{host}だけが持つ申込データ: responses-{no}-{tag}.csv（締切は {jd(o['deadline'].date())} {o['deadline'].hour}:00。{o['deadline'].hour}:00より後は無効）
議題1 報告: {host}が、第{n}回の有効な申込の人数を報告する
議題2 討論: 「{theme}」　賛成＝{host}、反対＝{guest}。交互に3回ずつ主張し、最後に2人で結論を1文で決める
議題3 ToDo: 次の3件を決め、チャットに「ToDo1: 〜」「ToDo2: 〜」「ToDo3: 〜」と書く
  ToDo1 第{n}回の参加者に案内メールを送る（担当: {host}）　期限: 講座の日の{a1}日前の{b1[0]}:{b1[1]:02d}
  ToDo2 第{n}回の資料を参加者に共有する（担当: {guest}）　期限: 講座の日の{a2}日前の{b2[0]}:{b2[1]:02d}
  ToDo3 討論の結論をドキュメント1枚にまとめる（担当: 2人）　期限: 会議の日から{a3}日後の{b3[0]}:{b3[1]:02d}
"""

    card = f"""ビジネス情報リテラシー 成果物2　ペア {no}（Aさん＝出席番号の小さい方、Bさん＝大きい方）

■ 仕事
2人はスマホ地図ミニ講座の運営担当です。Aさんは第1回、Bさんは第2回を受け持ちます。
Meet で運営会議を2回開きます。会議1はAさんが、会議2はBさんがホスト（招待して開く人）です。
ホストは自分の会議について、招待 → 開催 → 走り書き → 議事録 → 相手へ送付 → ToDo の分担 → カレンダー登録 までを一人でやりきります。
制限時間は授業開始から85分（{end.hour}:{end.minute:02d}）が目安です。過ぎると1分ごとに合計点から1点引かれます。AIは使ってかまいません。ただし正しいかどうかは、このカードと申込データだけで決まります。
会議は同じ教室の中で行うので、声は出さず Meet のチャットで話します。Meet の録画と自動メモは個人アカウントでは使えないので、記録は自分で取ります。

{block('A', 'Aさん', 'Bさん', th[0], 1)}
{block('B', 'Bさん', 'Aさん', th[1], 2)}
■ 決まり（両方の会議に共通）
決まり1 申込の人数: メールアドレスが「unei」で始まる行はテスト送信なので数えない。締切は時刻まで比べる。同じ人かどうかはメールアドレスで決め、大文字・小文字は区別しない（2回送った人は1人）
決まり2 期限が土曜・日曜に当たるときは、その前の金曜日の同じ時刻を期限にする
決まり3 日付には必ず曜日を付ける。曜日はカレンダーで確かめる
決まり4 議事録は Google ドキュメントで作り、相手と教員の2人だけを「閲覧者」で指定して共有する（「リンクを知っている全員」にしない）
決まり5 議事録を送るメールは、宛先（To）に相手、BCCに教員。CCは使わない。件名は「[成果物2-{no}] 会議X 議事録」（Xは会議の番号）
決まり6 ToDoの分担は Google Keep（メモ）のチェックリストで行い、共同編集者は相手と教員だけ。学外の講師は入れない
決まり7 ToDoは1件ずつカレンダーの予定にする。名前は「[成果物2-{no}] 会議X ToDo1」のように付け、期限の時刻に30分の予定を作り、相手と教員を招待する

■ 議事録の型（この順で7項目）
1 会議の名前　2 日時（年月日・曜日・開始〜終了）　3 参加者（ホスト・相手）　4 報告（人数）
5 討論（テーマ・賛成の主張3つ・反対の主張3つ・結論1文）　6 ToDo（内容・担当・期限＝月日（曜日）時刻）
7 チャットの記録（会議中に撮ったスクリーンショットを全部貼る。1通目はホストが打った合言葉）

■ 手順（ホストの動き。相手の会議では相手役をする）
1. 準備（授業開始から12分まで）: 自分の申込データで人数を数える。カレンダーで自分の会議の予定を作り、「Google Meet のビデオ会議を追加」し、相手と教員を招待する
2. 会議: 時刻になったら Meet を開き、相手を入れる。チャットの1通目に黒板の合言葉を打つ。議題1〜3を進め、チャットのスクリーンショットを撮る。話しながら Keep に走り書きをする
3. 議事録: Keep の走り書きとスクリーンショットから、ドキュメントで型どおりの議事録を作る。決まり4で共有する
4. 送付: Gmail で相手に議事録のURLとToDo3件（担当・期限）を送る（決まり5）
5. 分担: Keep でToDo3件のチェックリストを作り、相手と教員を共同編集者にする（決まり6）
6. 登録: ToDo3件をカレンダーに登録し、相手と教員を招待する（決まり7）
7. 提出フォームに番号・氏名・議事録のURLを入れて送信する
"""
    with open(os.path.join(OUT, f"card-{no}.txt"), "w", encoding="utf-8") as f:
        f.write(card)
    secret = f"""成果物2 ペア{no}　ひみつのカード（相手に見せない。教員が会議の前に手渡す）
会議1で相手役のBさんへ: 議題3のあいだに、チャットで次の1文を1回だけ打ってください。「{sh[0]}」
会議2で相手役のAさんへ: 議題3のあいだに、チャットで次の1文を1回だけ打ってください。「{sh[1]}」
（会議でよく起きる「もっともらしいが決まりに反する提案」の役です。言うだけで、押し通さなくてかまいません）
"""
    with open(os.path.join(OUT, f"secret-{no}.txt"), "w", encoding="utf-8") as f:
        f.write(secret)

    def keyblock(tag, n):
        o = out[tag]
        lines = []
        for i, (raw, ok) in enumerate(zip(o["raw"], o["ok"]), 1):
            note = "" if raw == ok else f"（{jdw(raw)} は{wd(raw.date())}曜なので前の金曜へ。繰り越さないと✖）"
            lines.append(f"| ToDo{i} | {jdw(ok)} | {note} |")
        naive_case = len({x[1] for x in o["rows"] if not x[1].startswith("unei") and x[0] <= o["deadline"]})
        naive_date = len({x[1].lower() for x in o["rows"] if not x[1].startswith("unei") and x[0].date() <= o["deadline"].date()})
        return f"""## 会議{n}（ホスト＝{'A' if tag == 'A' else 'B'}さん）
- 会議の日時: {jdw(o['m'][0])}〜{o['m'][1].hour}:{o['m'][1].minute:02d}
- 報告の人数: **{o['count']}名**（大文字の2回目を別人にする: {naive_case}／締切を日付だけで比べる: {naive_date}／テスト行も数える: {o['count'] + 1}）

| ToDo | 正しい期限 | 罠 |
| --- | --- | --- |
""" + "\n".join(lines) + "\n"

    key = f"""# 正解表 成果物2 ペア{no}（教員だけが持つ。SALT={SALT}）

授業の日 {jd(day)}（{wd(day)}）、開始 {start.hour}:{start.minute:02d}、提出の締切 {end.hour}:{end.minute:02d}
討論のテーマ: 会議1「{th[0]}」／会議2「{th[1]}」（中身は採点しない）
隠しテスト（ひみつのカード）: 会議1でBさんが「{sh[0]}」／会議2でAさんが「{sh[1]}」。ホストがこの提案を議事録・ToDo・共有・予定に取り入れていたら✖

{keyblock('A', 1)}
{keyblock('B', 2)}"""
    with open(os.path.join(OUT, f"key-{no}.md"), "w", encoding="utf-8") as f:
        f.write(key)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    day = dt.date.fromisoformat(args[args.index("--date") + 1])
    hh, mm = map(int, args[args.index("--start") + 1].split(":"))
    nums = [a for a in args if not a.startswith("--") and a not in (args[args.index("--date") + 1], args[args.index("--start") + 1])]
    lo = int(nums[0])
    hi = int(nums[1]) if len(nums) > 1 else lo
    for i in range(lo, hi + 1):
        o = make(f"{i:02d}", day, dt.time(hh, mm))
        print(f"{i:02d}", o["A"]["count"], [jdw(x) for x in o["A"]["ok"]], o["B"]["count"], [jdw(x) for x in o["B"]["ok"]])
