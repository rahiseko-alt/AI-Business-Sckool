"""成果物3「引き継いだ共有フォルダを整理して、人数を報告する」の番号版を作る。

使い方: LIT_SALT=秘密の語 python3 make.py 07      -> data/申込-07-*.csv / data/名簿-07.csv / kit-07.txt / key-07.md
        LIT_SALT=秘密の語 python3 make.py 1 40
番号で変わるのは申込の3ファイル（書き出し 11/03・11/10・11/16）と名簿。ほかは folder/（make_folder.py）で全員共通。
"""
import csv
import datetime as dt
import os
import random
import sys

SALT = os.environ.get("LIT_SALT", "demo-2026")
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("LIT_OUT", BASE)
TANTO = os.environ.get("ROLE_TANTO", "tanto.yaku@example.com")
KOSHI = os.environ.get("ROLE_KOSHI", "koshi.yaku@example.com")
SHISETSU = os.environ.get("ROLE_SHISETSU", "shisetsu.yaku@example.com")
INSATSU = os.environ.get("ROLE_INSATSU", "insatsu.yaku@example.com")
SEI = ["アオキ", "イシダ", "ウエノ", "エンドウ", "オオタ", "カトウ", "キムラ", "クボ", "コバヤシ", "サイトウ",
       "シミズ", "スギタ", "セキ", "タカギ", "チバ", "ツジ", "ナカノ", "ニシダ", "ノムラ", "ハヤシ",
       "ヒラノ", "フジタ", "ホンダ", "マツダ", "ミヤケ", "ムラタ", "モリ", "ヤノ", "ヨシダ", "ワダ"]
MEI = ["アオイ", "イツキ", "ウタ", "エマ", "カイ", "サク", "シオン", "スズ", "ソラ", "タクミ",
       "チヒロ", "ツバサ", "ナギ", "ヒナタ", "ホノカ", "マオ", "ミナト", "メイ", "ユイ", "リク"]
DEADLINE = dt.datetime(2026, 11, 16, 17, 0)
EXPORTS = [dt.datetime(2026, 11, 3, 8, 40), dt.datetime(2026, 11, 10, 9, 12), dt.datetime(2026, 11, 16, 18, 5)]
START = dt.datetime(2026, 10, 26, 9, 0)
CANCEL = ["キャンセルします", "都合が悪くなったのでキャンセルでお願いします"]


MEMO = """■ 運用メモ（前任者が残したもの。これが正しさの基準）
メモ1 名前は「動画講座_種類_MMDD」。種類は 申込・案内・名簿・チラシ・地図 のどれか。MMDD はファイルの中に書かれた日付（申込は「書き出し」、案内は「更新」、名簿は「作成」、チラシと地図は画像の中の日付）。ファイル名の「最終」「修正」は当てにしない
メモ2 中身がまったく同じファイルが2つあるときは、片方の名前の最後に「_重複」を付ける
メモ3 引き継ぎフォルダの直下に「最新」「旧版」の2つのフォルダを作る。種類ごとに日付がいちばん新しい1つを「最新」へ、残りはすべて「旧版」へ移す。ファイルは消さない。運用メモと「下見写真」フォルダは直下のまま
メモ4 「リンクを知っている全員」はどのファイルにも使わない。申込と名簿は学外の人（講師・印刷）に共有しない。講師には最新の案内だけを閲覧者で共有する
メモ5 人数: アドレスが「unei」で始まる行はテスト送信で数えない。締切は11月16日（月）17:00で、17:00より後に届いた行は無効（時刻まで比べる）。同じ人かどうかはメールアドレスで決め、大文字・小文字と前後の空白は区別しない。同じ人が何度も送ったときは、締切までのいちばん新しい回答だけを使い、その備考に「キャンセル」があれば取消
メモ6 下見写真は、Google フォトのアルバム「動画講座_下見」にして施設課と共有する。入れるのは 入口・教室・電源・掲示板 の4枚。人の顔が写った写真は使わない。人の名札が写っていたら、名札が写らないように切り取る。アルバムの共有相手は施設課だけ、リンクの共有はオフ、「写真の撮影場所を共有する」はオフ
メモ7 報告は次の担当者に1通。宛先（To）に担当者（CC・BCCなし）。件名「[成果物3-NN] 引き継ぎフォルダの整理と申込人数」。本文に、最新の申込のファイル名・有効な申込の人数・旧版に移したファイルの数・「最新」フォルダのリンクを書く。「最新」フォルダは担当者を閲覧者で指定して共有する
"""

KIT = """ビジネス情報リテラシー 成果物3　材料 NN番（この番号以外で出したものは採点しません）

■ 仕事
あなたは「スマホ動画ミニ講座」の運営を前任者から引き継ぎました。前任者の共有フォルダ「成果物3_NN_引き継ぎ」（教員が作り、あなたを編集者にしてあります）は散らかっています。
運用メモ（下）どおりにフォルダを整理し、下見写真を施設課に渡し、最新の申込から人数を数えて、次の担当者にメールで報告してください。
制限時間は45分。AIは使ってかまいません。ただし正しいかどうかは、運用メモとフォルダの中身だけで決まります。
相手のアドレス: 担当者 """ + TANTO + """／施設課 """ + SHISETSU + """／講師 """ + KOSHI + """／印刷 """ + INSATSU + """

""" + MEMO + """
■ 出すもの
(1) 整理したフォルダ（教員がオーナーなので、そのまま見ます）
(2) 自分のスプレッドシート「成果物3_NN_自分の氏名」: A1 に開始の合言葉、B1 テスト送信の行数、B2 締切後に届いた行数（テストを除く）、B3 有効な申込の人数（B列は数だけ）
(3) フォトのアルバム「動画講座_下見」（施設課と共有）
(4) 担当者への報告メール
(5) 画面録画（開始から提出フォームの送信画面まで止めない）。ドライブに上げ、教員だけを閲覧者にする
(6) 提出フォーム: シートのURL・録画のURL

■ 手順の目安
1. 画面録画を始め、シートを作り、A1に合言葉を入れる（2分）
2. フォルダの中身を1つずつ開き、中の日付を確かめて、シートの別のタブに一覧を作る（10分）
3. 「最新」「旧版」を作り、名前を直して移す。共有をメモ4に合わせる（10分）
4. 最新の申込で人数を数え、B1〜B3に入れる（8分）
5. 写真を端末に保存し、フォトでアルバムを作り、名札を切り取り、施設課と共有する（8分）
6. 報告メールを送り、「最新」フォルダを担当者と共有する（4分）
7. 録画を止めてドライブに上げ、共有して、提出フォームを送る（3分）
"""


def ts(t):
    return f"{t.year}/{t.month:02d}/{t.day:02d} {t.hour}:{t.minute:02d}:{t.second:02d}"


def build(no):
    r = random.Random(f"{SALT}-d3-{no}")
    n = r.randint(15, 19)
    names = r.sample([s + " " + m for s in SEI for m in MEI], n + 5)
    ids = r.sample(range(1000, 10000), n + 5)
    ppl = [(f"s{ids[i]}@example.com", names[i]) for i in range(n + 5)]
    span = int((DEADLINE - START).total_seconds())
    rows = []

    def t_in(lo, hi):
        return START + dt.timedelta(seconds=r.randint(int(lo * span), int(hi * span)))

    def add(t, mail, name, note=""):
        rows.append([t, mail, name, r.choice(["はい", "いいえ"]), note])

    for m, nm in ppl[:n]:
        add(t_in(0.0, 0.93), m, nm)
    # 重複2人: 大文字で送り直し／末尾に空白（電話で受けて手入力）
    a, b = r.sample(range(n), 2)
    add(t_in(0.94, 0.98), "S" + ppl[a][0][1:], ppl[a][1], "念のためもう一度送ります")
    add(t_in(0.94, 0.98), ppl[b][0] + " ", ppl[b][1], "電話受付")
    # 取消2人（1人は大文字でキャンセル）
    for j, (m, nm) in enumerate(ppl[n:n + 2]):
        add(t_in(0.05, 0.4), m, nm)
        add(t_in(0.5, 0.9), m if j == 0 else m.upper(), nm, r.choice(CANCEL))
    # 取消のあと申し込み直した人（最新は申込なので有効）
    m, nm = ppl[n + 2]
    add(t_in(0.05, 0.3), m, nm)
    add(t_in(0.35, 0.6), m, nm, r.choice(CANCEL))
    add(t_in(0.7, 0.95), m, nm, "やっぱり参加します")
    # テスト送信2行
    add(START + dt.timedelta(minutes=r.randint(3, 40)), "unei01@example.com", "テスト", "送信テスト")
    add(START + dt.timedelta(minutes=r.randint(45, 120)), "unei.check@example.com", "テスト 2", "動作確認")
    # 締切後2行: 17:0x の新しい人、17:3x〜17:5x の既存の人の送り直し
    m, nm = ppl[n + 3]
    add(DEADLINE + dt.timedelta(minutes=r.randint(1, 8), seconds=r.randint(1, 59)), m, nm)
    c = r.randrange(n)
    add(DEADLINE + dt.timedelta(minutes=r.randint(30, 55), seconds=r.randint(1, 59)), ppl[c][0], ppl[c][1], "念のためもう一度送ります")
    rows.sort(key=lambda x: x[0])
    return rows


def answers(rows):
    test = [x for x in rows if x[1].strip().lower().startswith("unei")]
    late = [x for x in rows if x not in test and x[0] > DEADLINE]
    ok = [x for x in rows if x not in test and x not in late]
    latest = {}
    for x in sorted(ok, key=lambda x: x[0]):
        latest[x[1].strip().lower()] = x
    valid = [x for x in latest.values() if "キャンセル" not in x[4]]
    return dict(B1=len(test), B2=len(late), B3=len(valid)), valid


def naive(rows):
    notest = [x for x in rows if not x[1].startswith("unei")]
    inday = [x for x in notest if x[0].date() <= DEADLINE.date()]
    ok = [x for x in notest if x[0] <= DEADLINE]
    lat = {}
    for x in sorted(ok, key=lambda x: x[0]):
        lat[x[1]] = x
    case = len([x for x in lat.values() if "キャンセル" not in x[4]])
    anyc = {x[1].strip().lower() for x in ok if "キャンセル" in x[4]}
    allp = {x[1].strip().lower() for x in ok}
    lat2 = {}
    for x in sorted(inday, key=lambda x: x[0]):
        lat2[x[1].strip().lower()] = x
    dateonly = len([x for x in lat2.values() if "キャンセル" not in x[4]])
    return dict(case=case, anycancel=len(allp - anyc), dateonly=dateonly,
                B2_dateonly=len(notest) - len(inday))


def hidden(rows, valid):
    """段5 隠しテスト: 動画講座_申込_1116 のコピーの最後に3行を足したときの正解。"""
    v0 = sorted(valid, key=lambda x: x[0])[0]
    extra = [[dt.datetime(2026, 11, 15, 10, 4, 12), "s0201@example.com", "オオノ アキ", "はい", ""],
             [dt.datetime(2026, 11, 16, 17, 1, 20), "s0202@example.com", "オオノ フユ", "いいえ", ""],
             [dt.datetime(2026, 11, 16, 16, 50, 5), v0[1].strip().upper() + " ", v0[2], "いいえ", "キャンセルします"]]
    a2, _ = answers(rows + extra)
    body = "\n".join(f"  {ts(x[0])},{x[1]},{x[2]},{x[3]},{x[4]}" for x in extra)
    return f"""
## 段5 隠しテスト（教員が 動画講座_申込_1116 のコピーを作り、データの最後に3行を足す）
{body}
足したあとの正解: B1={a2['B1']} B2={a2['B2']} B3={a2['B3']}（集計タブが式で数えていれば自動で変わる）
"""


def make(no):
    rows = build(no)
    a, valid = answers(rows)
    nv = naive(rows)
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
    olds = {}
    for e in EXPORTS:
        part = [x for x in rows if x[0] <= e]
        tag = f"{e.month:02d}{e.day:02d}"
        with open(os.path.join(OUT, "data", f"申込-{no}-{tag}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([f"書き出し: {e.year}/{e.month:02d}/{e.day:02d} {e.hour}:{e.minute:02d}", "", "", "", ""])
            w.writerow(["タイムスタンプ", "メールアドレス", "氏名（カナ）", "写真に写ってよい", "備考"])
            for x in part:
                w.writerow([ts(x[0]), x[1], x[2], x[3], x[4]])
        if e != EXPORTS[-1]:
            dl = DEADLINE if e > DEADLINE else e
            olds[tag] = answers([x for x in part if x[0] <= dl])[0]["B3"]
    with open(os.path.join(OUT, "data", f"名簿-{no}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["作成: 2026/11/12", "", ""])
        w.writerow(["受付番号", "氏名（カナ）", "メールアドレス"])
        for i, x in enumerate(sorted([x for x in valid if x[0] <= dt.datetime(2026, 11, 12)], key=lambda x: x[0]), 1):
            w.writerow([f"{i:03d}", x[2], x[1].strip().lower()])

    key = f"""# 正解表 成果物3 {no}番（教員だけが持つ。SALT={SALT}）

## 集計シート（学生のファイル「成果物3_{no}_氏名」）
| セル | 正解 | 罠に落ちたときの値 |
| --- | --- | --- |
| B1 テスト送信の行数 | {a['B1']} | |
| B2 締切後に届いた行数 | {a['B2']} | 日付だけで比べる: {nv['B2_dateonly']} |
| B3 有効な申込の人数 | {a['B3']} | 大文字・空白を区別: {nv['case']}／キャンセルが1度でもある人を除く: {nv['anycancel']}／締切を日付だけで比べる: {nv['dateonly']}／古いファイル（1110）で数える: {olds['1110']}／（1103）: {olds['1103']} |

## フォルダ（全員共通）
| 元の名前 | 正しい名前 | 置き場所 |
| --- | --- | --- |
| 申込一覧 | 動画講座_申込_1116 | 最新 |
| 申込一覧_最終版 | 動画講座_申込_1110 | 旧版 |
| 申込一覧_最終版 のコピー | 動画講座_申込_1110_重複 | 旧版 |
| 申込一覧(古い) | 動画講座_申込_1103 | 旧版 |
| 案内文_下書き_修正版 | 動画講座_案内_1113 | 最新 |
| 案内文_下書き | 動画講座_案内_1109 | 旧版 |
| 案内文_最終 | 動画講座_案内_1105 | 旧版 |
| 参加者名簿 | 動画講座_名簿_1112 | 最新 |
| チラシ_修正.png | 動画講座_チラシ_1108 | 最新 |
| チラシ.png | 動画講座_チラシ_1101 | 旧版 |
| 会場の地図.png | 動画講座_地図_1030 | 最新 |
| 運用メモ | 運用メモ（変えない） | 直下のまま |
| 下見写真（フォルダ、6枚） | 変えない | 直下のまま |

- 旧版に移すのは **6個**。「最新」は5個。消したファイルが1つでもあれば✖
- 共有（初期状態 → 正しい状態）:
  - チラシ.png: 「リンクを知っている全員が閲覧可」→ 制限付き（止める）
  - 参加者名簿: 印刷役 {INSATSU} が閲覧者 → 外す
  - 案内文_最終: 講師役 {KOSHI} が編集者 → 外す
  - 案内文_下書き_修正版: 講師役が閲覧者 → そのまま（外したら✖）

## アルバム「動画講座_下見」（Google フォト）
- 入れる4枚: IMG_3101（入口）・IMG_3102（教室）・IMG_3103（電源、右下の名札を切り取る）・IMG_3104（掲示板）
- 入れない: IMG_3105（人の顔が写っている）・IMG_3106（廊下、要らない）
- 共有: 施設課役 {SHISETSU} だけ。リンクの共有オフ。「写真の撮影場所を共有する」オフ

## 報告メール（担当役 {TANTO} に To。CC・BCCなし）
- 件名: [成果物3-{no}] 引き継ぎフォルダの整理と申込人数
- 本文に: 最新の申込のファイル名「動画講座_申込_1116」、有効な申込の人数 **{a['B3']}名**、旧版に移したファイルの数 **6**、「最新」フォルダのリンク
- 「最新」フォルダは担当役を閲覧者で指定して共有（リンクを知っている全員にしない）
""" + hidden(rows, valid)
    with open(os.path.join(OUT, f"key-{no}.md"), "w", encoding="utf-8") as f:
        f.write(key)
    with open(os.path.join(OUT, f"kit-{no}.txt"), "w", encoding="utf-8") as f:
        f.write(KIT.replace("NN", no))
    return a, nv, olds


if __name__ == "__main__":
    lo = int(sys.argv[1])
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else lo
    for i in range(lo, hi + 1):
        print(f"{i:02d}", *make(f"{i:02d}"))
