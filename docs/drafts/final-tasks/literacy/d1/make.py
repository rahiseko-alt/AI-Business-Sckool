"""成果物1「日程変更の連絡に返信する」の番号版を作る。

使い方: LIT_SALT=秘密の語 python3 make.py 07       -> kit-07.txt / key-07.md
        LIT_SALT=秘密の語 python3 make.py 1 40     -> 01〜40
役のアドレス（教員が用意したテスト用アカウント）は環境変数で入れる:
  ROLE_KOSHI（講師役） ROLE_SHISETSU（施設課役） ROLE_INSATSU（印刷役）
学生に配るのは kit-NN.txt だけ。key-NN.md は教員だけが持つ。
"""
import datetime as dt
import os
import random
import sys

SALT = os.environ.get("LIT_SALT", "demo-2026")
OUT = os.environ.get("LIT_OUT", os.path.dirname(os.path.abspath(__file__)))
KOSHI = os.environ.get("ROLE_KOSHI", "koshi.yaku@example.com")
SHISETSU = os.environ.get("ROLE_SHISETSU", "shisetsu.yaku@example.com")
INSATSU = os.environ.get("ROLE_INSATSU", "insatsu.yaku@example.com")
WD = "月火水木金土日"
ROOMS = ["B棟1階105教室", "C棟2階204教室", "D棟3階302教室", "B棟2階201教室", "C棟1階103教室"]
KOSHI_NAME = ["ミヤケ", "タカギ", "ホンダ", "ムラタ", "チバ", "キムラ"]
SHISETSU_NAME = ["モリ", "ツジ", "ハヤシ", "イシダ", "ウエノ"]


def wd(d):
    return WD[d.weekday()]


def jd(d):
    return f"{d.month}月{d.day}日"


def hm(t):
    return f"{t.hour}:{t.minute:02d}"


def build(no):
    r = random.Random(f"{SALT}-d1-{no}")
    firsts = [dt.date(2026, 11, d) for d in range(2, 14) if dt.date(2026, 11, d).weekday() < 5]
    p1 = r.choice(firsts)
    p2 = p1 + dt.timedelta(days=7)
    wrong = WD[(p2.weekday() + 1) % 7]  # 講師がメールに書いた誤った曜日
    delta = r.choice([10, 20, 30])
    s0 = dt.datetime(2026, 1, 1, 16, 20)
    e0 = dt.datetime(2026, 1, 1, 17, 30)
    s1, e1 = s0 + dt.timedelta(minutes=delta), e0 + dt.timedelta(minutes=delta)
    room0 = "A棟2階201教室"
    room1 = r.choice(ROOMS)
    k, s = r.choice(KOSHI_NAME), r.choice(SHISETSU_NAME)
    m1 = dt.datetime(2026, 10, r.randint(13, 16), r.randint(9, 11), r.randint(0, 59))
    m2 = m1 + dt.timedelta(days=1, hours=r.randint(1, 5), minutes=r.randint(0, 59))
    m3 = m2 + dt.timedelta(hours=r.randint(2, 20), minutes=r.randint(0, 59))
    m4 = m3 + dt.timedelta(hours=r.randint(2, 20), minutes=r.randint(0, 59))
    return dict(no=no, p1=p1, p2=p2, wrong=wrong, delta=delta, s0=s0, e0=e0, s1=s1, e1=e1,
                room0=room0, room1=room1, k=k, s=s, m=[m1, m2, m3, m4])


def stamp(t):
    return f"2026/{t.month:02d}/{t.day:02d}（{wd(t.date())}）{t.hour}:{t.minute:02d}"


def make(no):
    v = build(no)
    p1, p2, m = v["p1"], v["p2"], v["m"]
    unei = "unei.maeda@example.com"
    subj = f"【日程確定】スマホ写真ミニ講座（成果物1-{no}）"
    thread = f"""--- メール1 ---
差出人: 前田（前任の運営担当） <{unei}>
宛先: {v['k']} 様（講師） <{KOSHI}>
CC: {v['s']} 様（施設課） <{SHISETSU}>, 印刷担当 <{INSATSU}>
日時: {stamp(m[0])}
件名: スマホ写真ミニ講座の日程について

{v['k']} 様
いつもお世話になっております。運営の前田です。
スマホ写真ミニ講座を、{jd(p1)}（{wd(p1)}）{hm(v['s0'])}〜{hm(v['e0'])}、{v['room0']}で開きたいと考えています。
ご都合はいかがでしょうか。施設課と印刷担当にもCCでお送りしています。

--- メール2 ---
差出人: {v['k']}（講師） <{KOSHI}>
宛先: 前田 <{unei}>
CC: {v['s']} 様（施設課） <{SHISETSU}>, 印刷担当 <{INSATSU}>
日時: {stamp(m[1])}
件名: Re: スマホ写真ミニ講座の日程について

前田さん
ご連絡ありがとうございます。{jd(p1)}は別の予定が入っています。
翌週の{jd(p2)}（{v['wrong']}）の同じ時間なら伺えます。

--- メール3 ---
差出人: {v['s']}（施設課） <{SHISETSU}>
宛先: 前田 <{unei}>
CC: {v['k']} 様（講師） <{KOSHI}>, 印刷担当 <{INSATSU}>
日時: {stamp(m[2])}
件名: Re: Re: スマホ写真ミニ講座の日程について

前田さん
{jd(p2)}は{v['room0']}が点検で使えません。同じ時間なら{v['room1']}をお取りできます。

--- メール4 ---
差出人: {v['k']}（講師） <{KOSHI}>
宛先: 前田 <{unei}>
日時: {stamp(m[3])}
件名: Re: Re: Re: スマホ写真ミニ講座の日程について

前田さん（このメールは前田さんだけにお送りしています）
{v['room1']}で大丈夫です。ただ、当日は前の予定が延びそうなので、
開始と終了をそれぞれ{v['delta']}分ずつ遅らせていただけると助かります。
"""
    kit = f"""ビジネス情報リテラシー 成果物1　材料 {no}番（この番号以外の材料で出したものは採点しません）

■ 仕事
あなたは学内の「スマホ写真ミニ講座」の運営担当を、前任の前田さんから今日引き継ぎました。
前田さんの受信箱に、講座の日程を決めるメールのやり取り（下のメール1〜4）が残っています。
このやり取りで決まった日時と会場を、講師と施設課に知らせる「日程確定のメール」を、あなたの Gmail から1通送ってください。
制限時間は20分。AIは使ってかまいません。ただし正しいかどうかは、この紙の「運営の決まり」とメール1〜4だけで決まります。
時間を過ぎると、提出フォームの時刻が制限20分を過ぎた分、1分ごとに合計点から1点を引きます（0点より下にはなりません）。

■ 運営の決まり
決まり1 日時と会場は、やり取りの中でいちばん新しい合意に従う。あとのメールが前のメールを上書きする
決まり2 曜日はカレンダーで確かめて書く。メールに書かれた曜日を写さない
決まり3 学外の人（講師）と学内の人（施設課）に一緒に送るメールは、2人とも「BCC」に入れ、「宛先（To）」は自分にする。CCは使わない
決まり4 印刷担当には、資料が決まってから別に連絡する。今回のメールには入れない
決まり5 件名は「{subj}」にする

■ 送るメールの中身（この3行を本文に必ず入れる。ほかの文は自由）
日にち：〔月日（曜日）〕
時間：〔開始〜終了〕
会場：〔建物・階・教室〕

■ 手順
1. 下のメール1〜4を読み、決まり1〜4に照らして、日にち・曜日・時間・会場・送る相手を決める
2. Gmail で新しいメールを作る（「全員に返信」は使わない）。宛先は自分、BCCに講師と施設課のアドレス
3. 件名と本文を書き、送信する
4. 送信済みフォルダで、宛先・BCC・件名・本文をもう一度確かめる
5. 提出フォームに番号と氏名を入れて送信する（フォームはメールアドレスを記録する）

■ 前田さんの受信箱に残っていたメール
{thread}"""
    with open(os.path.join(OUT, f"kit-{no}.txt"), "w", encoding="utf-8") as f:
        f.write(kit)
    key = f"""# 正解表 成果物1 {no}番（教員だけが持つ。SALT={SALT}）

## 正しいメール
- 件名: {subj}
- 宛先(To): 学生本人のアドレス／CC: なし／BCC: 講師役 {KOSHI}・施設課役 {SHISETSU}
- 印刷役 {INSATSU} には届いていない
- 本文の3行:
  - 日にち：{jd(p2)}（{wd(p2)}）
  - 時間：{hm(v['s1'])}〜{hm(v['e1'])}
  - 会場：{v['room1']}

## 罠に落ちたときの値
| 項目 | 正解 | 落ちたときの値 | 落ちる理由 |
| --- | --- | --- | --- |
| 日にち | {jd(p2)} | {jd(p1)} | メール1の案を使った |
| 曜日 | {wd(p2)} | {v['wrong']} | メール2の曜日を写した（決まり2） |
| 時間 | {hm(v['s1'])}〜{hm(v['e1'])} | {hm(v['s0'])}〜{hm(v['e0'])} | メール4（前田さんだけに届いた）を見落とした |
| 会場 | {v['room1']} | {v['room0']} | メール3を見落とした |
| 送り方 | 講師・施設課ともBCC、Toは自分 | 講師がTo・施設課がCC | 決まり3 |
| 印刷役 | 届かない | 届く | 「全員に返信」を使った（決まり4） |
"""
    with open(os.path.join(OUT, f"key-{no}.md"), "w", encoding="utf-8") as f:
        f.write(key)
    return v


if __name__ == "__main__":
    lo = int(sys.argv[1])
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else lo
    for i in range(lo, hi + 1):
        v = make(f"{i:02d}")
        print(v["no"], jd(v["p2"]), wd(v["p2"]), hm(v["s1"]), hm(v["e1"]), v["room1"])
