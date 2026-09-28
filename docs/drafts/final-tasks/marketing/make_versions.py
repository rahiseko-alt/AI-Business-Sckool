# -*- coding: utf-8 -*-
"""マーケティング最終課題: 番号版の回答データと正解表を作り、正解を検算する。

使い方: python3 make_versions.py [人数]   （既定 40）
出力:  data/responses-NN.csv（学生に1人1つ渡す）
       05_正解表_教員用.csv（学生に渡さない）
同じ番号からは毎回同じデータができる（乱数の種＝番号）。年度を変えるときは SALT を変える。
"""
import csv
import datetime as dt
import os
import random
import sys
from decimal import Decimal, ROUND_HALF_UP

SALT = 2026
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- 材料と同じ定義（01〜04 の md と一字一句そろえる） ----
Q = {
    "q1": "ニックネームを書いてください",
    "q2": "みなと日本語カフェに来たことがありますか",
    "q3": "出身の国・地域を選んでください",
    "q4": "ふだん使うSNSをすべて選んでください",
    "q5": "次の場面で、日本語に困りますか",
    "q6": "参加しやすい時間をすべて選んでください",
    "q7": "日本語で話す自信はどのくらいですか",
    "q8": "前回のカフェの満足度を星で教えてください（来たことがある人だけ）",
    "q9": "次に来られそうな日を選んでください",
    "q10": "SNSをいちばんよく見る時刻を教えてください",
    "q11": "カフェでやってみたいことを自由に書いてください",
    "q12": "日本語で困った場面の写真やスクリーンショットがあれば送ってください（任意）",
}
COUNTRIES = ["日本", "中国", "韓国", "台湾", "ベトナム", "ネパール", "ミャンマー", "インドネシア",
             "フィリピン", "タイ", "スリランカ", "モンゴル", "ウズベキスタン", "その他"]
SNS = ["Instagram", "TikTok", "Facebook", "X", "YouTube", "LINE"]
CAROUSEL_SNS = ["Instagram", "TikTok", "Facebook"]  # 5枚を1投稿にできるもの（02_企画ルール）
SCENES = ["アルバイト", "学校", "病院", "役所"]
LEVELS = ["よく困る", "ときどき困る", "困らない"]
DAYS = ["平日", "土曜", "日曜"]
TIMES = ["午前", "午後", "夜"]
SLOTS = [(d, t) for d in DAYS for t in TIMES]
SLOT_TIME = {"午前": "10:00〜11:30", "午後": "14:00〜15:30", "夜": "19:00〜20:30"}
STAFF = "cafe-staff@example.com"
OPEN = dt.datetime(2026, 11, 20, 9, 0)
CLOSE = dt.datetime(2026, 11, 30, 23, 59, 59)
WISH = ["アルバイトの面接の練習", "敬語で電話する練習", "病院で症状を言う練習", "役所の書類の書き方",
        "友達を作りたい", "日本の料理の話", "発音をなおしたい", "学校の先生への話し方", ""]

# ---- 04_会場の予定.md と同じ表（2027年1月）。✖ は使えない ----
HOLIDAYS = {dt.date(2027, 1, 11)}  # 成人の日
CLOSED = {dt.date(2027, 1, 1), dt.date(2027, 1, 2), dt.date(2027, 1, 3)}  # 年始休館
NG = set()
for day in range(4, 9):
    NG.add((dt.date(2027, 1, day), "夜"))          # 1/4〜1/8 夜は点検
for day in range(4, 7):
    NG.add((dt.date(2027, 1, day), "午前"))        # 1/4〜1/6 午前は他団体
NG.add((dt.date(2027, 1, 4), "午後"))
NG |= {(dt.date(2027, 1, 9), "午前"), (dt.date(2027, 1, 9), "夜"),
       (dt.date(2027, 1, 10), "午後"), (dt.date(2027, 1, 10), "夜")}
CAL_DAYS = [dt.date(2027, 1, 1) + dt.timedelta(i) for i in range(24)]  # 1/1〜1/24
WD = "月火水木金土日"


def fmt_date(d):
    return f"{d.month}月{d.day}日（{WD[d.weekday()]}）"


def day_type(d):
    if d.weekday() == 5:
        return "土曜"
    if d.weekday() == 6:
        return "日曜"
    return None if d in HOLIDAYS else "平日"


def first_date(slot, ignore_holiday=False):
    """その曜日・時間帯で会場が○の最初の日。ignore_holiday=True は祝日を平日に数える誤り。"""
    dname, tname = slot
    for d in CAL_DAYS:
        if d in CLOSED or (d, tname) in NG:
            continue
        typ = day_type(d)
        if ignore_holiday and d in HOLIDAYS:
            typ = "平日"
        if typ == dname:
            return d
    raise ValueError(slot)


def r_half_up(x, nd=0):
    q = Decimal(1).scaleb(-nd)
    return Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP)


def argmax_unique(counter):
    top = max(counter.values())
    keys = [k for k, v in counter.items() if v == top]
    return keys[0] if len(keys) == 1 else None


# ---- 1人分の回答を作る ----
def person(rng, *, attended, country, scene_bias, slot_bias, sns_bias, hour_bias, star_trap):
    a = {"q1": rng.choice(["ミン", "アン", "リオ", "ソラ", "ハル", "ナナ", "ケイ", "ルカ", "トモ", "ユイ",
                            "ジョー", "マイ", "カイ", "レン", "サム", "ニコ", "ビビ", "タオ", "ララ", "ポン"])}
    a["q2"] = "はい" if attended else "いいえ"
    a["q3"] = country
    chosen = [s for s in SNS if rng.random() < {"LINE": 0.9, "YouTube": 0.45}.get(s, 0.25)
              + (0.45 if s == sns_bias else 0)]
    if not chosen:
        chosen = ["LINE"]
    a["q4"] = ", ".join(chosen)
    for sc in SCENES:
        p = 0.62 if sc == scene_bias else 0.22
        r = rng.random()
        a["q5_" + sc] = "よく困る" if r < p else ("ときどき困る" if r < p + 0.4 * (1 - p) else "困らない")
    for dname in DAYS:
        picks = [t for t in TIMES if rng.random() < (0.72 if (dname, t) == slot_bias else 0.2)]
        a["q6_" + dname] = ", ".join(picks)
    a["q7"] = str(rng.choice([1, 1, 2, 2, 2, 3, 3, 4, 5]) if not attended else rng.choice([2, 3, 3, 4, 4, 5]))
    if attended:
        a["q8"] = str(rng.choice([3, 4, 4, 4, 5, 5]))
    else:
        a["q8"] = str(rng.choice([1, 2, 2, 3])) if rng.random() < star_trap else ""
    d = dt.date(2027, 1, 4) + dt.timedelta(rng.randrange(0, 21))
    a["q9"] = d.strftime("%Y/%m/%d")
    h = hour_bias if rng.random() < 0.45 else rng.choice([7, 8, 12, 18, 20, 21, 22, 23])
    a["q10"] = f"{h}:{rng.randrange(0, 60):02d}:00"
    a["q11"] = rng.choice(WISH)
    a["q12"] = f"https://drive.google.com/open?id=EXAMPLE{rng.randrange(1000, 9999)}" if rng.random() < 0.12 else ""
    return a


HEADER = (["タイムスタンプ", "メールアドレス", Q["q1"], Q["q2"], Q["q3"], Q["q4"]]
          + [f"{Q['q5']} [{s}]" for s in SCENES]
          + [f"{Q['q6']} [{d}]" for d in DAYS]
          + [Q["q7"], Q["q8"], Q["q9"], Q["q10"], Q["q11"], Q["q12"]])


def to_row(ts, email, a):
    return ([ts.strftime("%Y/%m/%d %H:%M:%S"), email, a["q1"], a["q2"], a["q3"], a["q4"]]
            + [a["q5_" + s] for s in SCENES] + [a["q6_" + d] for d in DAYS]
            + [a["q7"], a["q8"], a["q9"], a["q10"], a["q11"], a["q12"]])


# ---- 集計（正しいやり方と、よくある誤り） ----
def analyze(rows, clean=True):
    """rows: [(行番号, dict)]。clean=True で 02_企画ルールの除外を全部行う。"""
    excluded = {}
    valid = []
    last_row_of = {}
    for n, r in rows:
        last_row_of[r["メールアドレス"]] = n
    for n, r in rows:
        ts = dt.datetime.strptime(r["タイムスタンプ"], "%Y/%m/%d %H:%M:%S")
        if clean:
            if r["メールアドレス"] == STAFF:
                excluded[n] = "テスト"; continue
            if ts > CLOSE:
                excluded[n] = "締切後"; continue
            if last_row_of[r["メールアドレス"]] != n:
                excluded[n] = "重複（古い方）"; continue
            if r[Q["q3"]] == "日本":
                excluded[n] = "対象外（日本）"; continue
        valid.append(r)
    tgt = [r for r in valid if r[Q["q2"]] == "いいえ"]
    att = [r for r in valid if r[Q["q2"]] == "はい"]

    def scene_counts(group):
        return {s: sum(r[f"{Q['q5']} [{s}]"] == "よく困る" for r in group) for s in SCENES}

    def slot_counts(group):
        c = {}
        for (d, t) in SLOTS:
            c[(d, t)] = sum(t in [x.strip() for x in r[f"{Q['q6']} [{d}]"].split(",")] for r in group)
        return c

    def sns_counts(group, exact=False):
        c = {}
        for s in SNS:
            if exact:
                c[s] = sum(r[Q["q4"]] == s for r in group)
            else:
                c[s] = sum(s in [x.strip() for x in r[Q["q4"]].split(",")] for r in group)
        return c

    def hour_counts(group):
        c = {}
        for r in group:
            h = int(r[Q["q10"]].split(":")[0])
            c[h] = c.get(h, 0) + 1
        return c

    return dict(valid=valid, tgt=tgt, att=att, excluded=excluded, scene_counts=scene_counts,
                slot_counts=slot_counts, sns_counts=sns_counts, hour_counts=hour_counts)


def make_version(no):
    base = random.Random(SALT * 100 + no)
    scene_t = SCENES[(no - 1) % 4]
    scene_a = SCENES[(no + 1) % 4]
    slot_t = SLOTS[(no * 2) % 9]
    slot_a = SLOTS[(no * 2 + 4) % 9]
    sns_t = CAROUSEL_SNS[(no - 1) % 3]
    hour_t = [21, 22, 12, 20, 23, 7][(no - 1) % 6]
    for attempt in range(5000):
        rng = random.Random(base.random())
        n_unique = rng.randint(36, 44)
        people = []
        for i in range(n_unique):
            attended = rng.random() < 0.4
            country = rng.choice(COUNTRIES[1:])
            if attended:
                a = person(rng, attended=True, country=country, scene_bias=scene_a, slot_bias=slot_a,
                           sns_bias=rng.choice(["LINE", "YouTube", "X"]), hour_bias=rng.choice([8, 18]), star_trap=0)
            else:
                a = person(rng, attended=False, country=country, scene_bias=scene_t, slot_bias=slot_t,
                           sns_bias=sns_t, hour_bias=hour_t, star_trap=0.35)
            ts = OPEN + dt.timedelta(minutes=rng.randrange(0, int((CLOSE - OPEN).total_seconds() // 60)))
            people.append([ts, f"u{i + 1:03d}@example.com", a])
        # 罠: 日本出身（対象外）を2〜3人
        for p in rng.sample(people, rng.choice([2, 3])):
            p[2]["q3"] = "日本"
        records = [(p[0], p[1], p[2]) for p in people]
        # 罠: 締切後の回答（来たことがない人）2件
        for j in range(2):
            a = person(rng, attended=False, country=rng.choice(COUNTRIES[1:]), scene_bias=scene_a,
                       slot_bias=slot_a, sns_bias="X", hour_bias=hour_t, star_trap=0.5)
            records.append((dt.datetime(2026, 12, 1, rng.randrange(0, 10), rng.randrange(60)),
                            f"u{n_unique + j + 1:03d}@example.com", a))
        # 罠: 重複（同じ人が前に一度出した古い回答）3件。古い方は「いいえ」で、別の場面・時間を選んでいる
        for p in rng.sample([p for p in people if p[2]["q3"] != "日本"], 3):
            a = person(rng, attended=False, country=p[2]["q3"], scene_bias=scene_a, slot_bias=slot_a,
                       sns_bias="X", hour_bias=hour_t, star_trap=0.8)
            a["q1"] = p[2]["q1"]
            records.append((p[0] - dt.timedelta(hours=rng.randrange(2, 48)), p[1], a))
        # 罠: 運営のテスト送信2件（開始前）
        for j in range(2):
            a = person(rng, attended=bool(j), country="その他", scene_bias=scene_a, slot_bias=slot_a,
                       sns_bias="LINE", hour_bias=9, star_trap=1)
            a["q1"] = "テスト"
            records.append((dt.datetime(2026, 11, 19, 17, 10 + j * 7), STAFF, a))
        records = [r for r in records if r[0] >= dt.datetime(2026, 11, 19)]
        records.sort(key=lambda r: r[0])
        table = [dict(zip(HEADER, to_row(*r))) for r in records]
        rows = [(i + 2, r) for i, r in enumerate(table)]  # スプレッドシートの行番号（1行目は見出し）

        ok = analyze(rows, clean=True)
        raw = analyze(rows, clean=False)
        tgt, att, valid = ok["tgt"], ok["att"], ok["valid"]
        sc_t = ok["scene_counts"](tgt)
        sc_all = ok["scene_counts"](valid)
        sl_t = ok["slot_counts"](tgt)
        sl_all = ok["slot_counts"](valid)
        sn_t = ok["sns_counts"](tgt)
        sn_t4 = {s: sn_t[s] for s in CAROUSEL_SNS}
        sn_t_withx = {s: sn_t[s] for s in CAROUSEL_SNS + ["X"]}
        hr_t = ok["hour_counts"](tgt)
        stars = [int(r[Q["q8"]]) for r in att if r[Q["q8"]]]
        stars_all = [int(r[Q["q8"]]) for r in valid if r[Q["q8"]]]
        stars_raw = [int(r[Q["q8"]]) for r in raw["valid"] if r[Q["q8"]]]
        S = argmax_unique(sc_t)
        SL = argmax_unique(sl_t)
        SN = argmax_unique(sn_t4)
        H = argmax_unique(hr_t)
        if None in (S, SL, SN, H) or not stars or not stars_all:
            continue
        conds = [
            S == scene_t, argmax_unique(sc_all) not in (None, S),  # 全員で数えると場面が変わる
            SL == slot_t, argmax_unique(sl_all) not in (None, SL),  # 全員で数えると時間帯が変わる
            SN == sns_t, sn_t["LINE"] > sn_t[SN],                  # LINE が最多（投稿先にはならない）
            argmax_unique(sn_t_withx) is not None,
            H == hour_t,
            len(stars) >= 5,
            r_half_up(sum(stars) / len(stars), 1) != r_half_up(sum(stars_all) / len(stars_all), 1),
            r_half_up(sum(stars) / len(stars), 1) != r_half_up(sum(stars_raw) / len(stars_raw), 1),
            len(raw["tgt"]) != len(tgt),
            len(tgt) >= 18,
            sn_t["X"] > sn_t[SN] or no % 3 != 0,  # 3の倍数の番号では X が投稿先より多い（X は4枚まで）
        ]
        if all(conds):
            break
    else:
        raise RuntimeError(f"no version for {no}")

    B2 = len(tgt)
    B4 = sc_t[S]
    B5 = int(r_half_up(B4 / B2 * 100))
    B10 = r_half_up(sum(stars) / len(stars), 1)
    date = first_date(SL)
    deadline = date - dt.timedelta(days=3)
    wrong_date = first_date(SL, ignore_holiday=True)
    key = {
        "番号": f"{no:02d}",
        "B1_有効回答": len(valid),
        "B2_ターゲット": B2,
        "B3_場面": S,
        "B4_よく困る人数": B4,
        "B5_割合%": B5,
        "B6_投稿先": SN,
        "B7_投稿時間帯": f"{H}時台",
        "B8_曜日時間帯": f"{SL[0]}{SL[1]}",
        "B9_選んだ人数": sl_t[SL],
        "B10_満足度": str(B10),
        "B11_満足度の人数": len(stars),
        "B12_最初の回": f"{fmt_date(date)} {SLOT_TIME[SL[1]]}",
        "B13_申込締切": fmt_date(deadline),
        "B14_除外した行": " ".join(str(n) for n in sorted(ok["excluded"])),
        "除外の内訳": " ".join(f"{n}:{why}" for n, why in sorted(ok["excluded"].items())),
        # よくある誤り（採点で「どの罠で落ちたか」を見分ける）
        "誤_掃除なし_B1": len(raw["valid"]),
        "誤_掃除なし_B2": len(raw["tgt"]),
        "誤_全員で数えた場面": argmax_unique(sc_all),
        "誤_全員で数えた時間帯": "".join(argmax_unique(sl_all)),
        "誤_LINEやXを含めた投稿先": argmax_unique(sn_t_withx | {"LINE": sn_t["LINE"]}),
        "誤_いいえの星も入れた満足度": str(r_half_up(sum(stars_all) / len(stars_all), 1)),
        "誤_掃除なしの満足度": str(r_half_up(sum(stars_raw) / len(stars_raw), 1)),
        "誤_祝日を平日に数えた日": fmt_date(wrong_date) if wrong_date != date else "",
    }
    return HEADER, table, key


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    keys = []
    for no in range(1, n + 1):
        header, table, key = make_version(no)
        with open(os.path.join(HERE, "data", f"responses-{no:02d}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=header)
            w.writeheader()
            w.writerows(table)
        keys.append(key)
    with open(os.path.join(HERE, "05_正解表_教員用.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(keys[0].keys()))
        w.writeheader()
        w.writerows(keys)
    # 検算: 保存したCSVを読み直し、独立に数え直して正解表と一致するか
    for k in keys:
        with open(os.path.join(HERE, "data", f"responses-{k['番号']}.csv"), encoding="utf-8") as f:
            rows = [(i + 2, r) for i, r in enumerate(csv.DictReader(f))]
        ok = analyze(rows)
        assert len(ok["valid"]) == k["B1_有効回答"]
        assert len(ok["tgt"]) == k["B2_ターゲット"]
        assert ok["scene_counts"](ok["tgt"])[k["B3_場面"]] == k["B4_よく困る人数"]
        assert len(rows) == len(ok["valid"]) + len(k["B14_除外した行"].split())
    # 会場の予定: 9つの時間帯の最初の回と締切
    print("時間帯ごとの最初の回（会場の予定から）")
    for s in SLOTS:
        d = first_date(s)
        print(f"  {s[0]}{s[1]}: {fmt_date(d)} 締切 {fmt_date(d - dt.timedelta(days=3))}"
              + (f"  ※祝日を平日に数えると {fmt_date(first_date(s, True))}" if first_date(s, True) != d else ""))
    print(f"{n}人分を作成。検算 OK")


if __name__ == "__main__":
    main()
