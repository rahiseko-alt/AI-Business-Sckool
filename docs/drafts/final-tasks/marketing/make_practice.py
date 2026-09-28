# -*- coding: utf-8 -*-
"""マーケティング成果物1〜4（d1〜d4）の番号版データと正解表を作る。

どれも「調査 → 集計 → 企画 → カルーセル」の一連の仕事。段階ごとに、設問の形式・行数・罠・条件を増やす。
使い方: python3 make_practice.py [人数]   （既定 40）
出力:  d1〜d4/data/responses-NN.csv、d1〜d4/05_正解表_教員用.csv
検算は verify_practice.py（別の書き方で数え直す）。
"""
import csv
import datetime as dt
import os
import random
import sys
from decimal import Decimal, ROUND_HALF_UP

SALT = 2026
HERE = os.path.dirname(os.path.abspath(__file__))
WD = "月火水木金土日"
STAFF = "cafe-staff@example.com"
NICK = ["ミン", "アン", "リオ", "ソラ", "ハル", "ナナ", "ケイ", "ルカ", "トモ", "ユイ", "ジョー", "マイ",
        "カイ", "レン", "サム", "ニコ", "ビビ", "タオ", "ララ", "ポン"]
COUNTRIES = ["日本", "中国", "韓国", "台湾", "ベトナム", "ネパール", "ミャンマー", "インドネシア",
             "フィリピン", "タイ", "スリランカ", "モンゴル", "ウズベキスタン", "その他"]
WISH = ["ゆっくり話したい", "友達を作りたい", "発音をなおしたい", "敬語を覚えたい", "ロールプレイをしたい", ""]


def fd(d):
    return f"{d.month}月{d.day}日（{WD[d.weekday()]}）"


def rhu(x, nd=0):
    return Decimal(str(x)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)


def top1(counter):
    best = max(counter.values())
    ks = [k for k, v in counter.items() if v == best]
    return ks[0] if len(ks) == 1 else None


def split(cell):
    return [x.strip() for x in cell.split(",") if x.strip()]


def ts_between(rng, a, b):
    return a + dt.timedelta(minutes=rng.randrange(int((b - a).total_seconds() // 60)))


def write(level, header, rows_by_no, keys):
    base = os.path.join(HERE, level)
    os.makedirs(os.path.join(base, "data"), exist_ok=True)
    for no, rows in rows_by_no.items():
        with open(os.path.join(base, "data", f"responses-{no:02d}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
    with open(os.path.join(base, "05_正解表_教員用.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(keys[0].keys()))
        w.writeheader()
        w.writerows(keys)


# ================= d1: 防災の日本語ワークショップ（3問・テスト送信だけ） =================
D1_Q = ["ニックネームを書いてください", "日本で地震にあったことがありますか", "知りたい防災の日本語をすべて選んでください"]
D1_OPT = ["避難所の場所を聞く", "けがを伝える", "家族の無事を伝える", "ニュースを聞き取る", "119番に電話する"]
D1_OPEN, D1_CLOSE = dt.datetime(2026, 10, 1, 9), dt.datetime(2026, 10, 7, 23, 59, 59)


def d1(no):
    rng = random.Random(SALT * 10 + no)
    t, s = D1_OPT[(no - 1) % 5], D1_OPT[no % 5]
    for _ in range(5000):
        n = rng.randint(10, 17)
        c = rng.randint(n // 2, n // 2 + 3)
        cnt = {o: rng.randint(1, c - 2) for o in D1_OPT}
        cnt[t], cnt[s] = c, c - 1
        picks = [set() for _ in range(n)]
        for o, k in cnt.items():
            for i in rng.sample(range(n), k):
                picks[i].add(o)
        if all(picks):
            break
    rows = []
    for i in range(n):
        rows.append([ts_between(rng, D1_OPEN, D1_CLOSE), f"u{i + 1:03d}@example.com", rng.choice(NICK),
                     rng.choice(["はい", "いいえ"]), ", ".join(o for o in D1_OPT if o in picks[i])])
    for j in range(2):  # 罠: 運営のテスト送信。2行とも s を選ぶ → 数えると s が最多になる
        rows.append([dt.datetime(2026, 9, 30, 17, 5 + j * 4), STAFF, "テスト", "いいえ", ", ".join([s, D1_OPT[(no + 2) % 5]])])
    rows.sort(key=lambda r: r[0])
    rows = [[r[0].strftime("%Y/%m/%d %H:%M:%S")] + r[1:] for r in rows]
    key = {"番号": f"{no:02d}", "B1_有効回答": n, "B2_知りたい日本語": t, "B3_人数": c,
           "誤_テストを数えたB1": n + 2, "誤_テストを数えた最多": s}
    return rows, key


# ================= d2: 電話の日本語練習会（6問・テスト送信と重複） =================
D2_Q = ["ニックネームを書いてください", "出身の国・地域を選んでください", "電話でいちばん困る相手を1つ選んでください",
        "電話で困ることをすべて選んでください", "電話で話す自信はどのくらいですか", "練習会でやってみたいことを自由に書いてください"]
D2_WHO = ["アルバイト先", "病院", "学校", "役所"]
D2_WHAT = ["聞き取れない", "敬語が分からない", "名前をうまく言えない", "番号を聞き返せない", "緊張する"]
D2_OPEN, D2_CLOSE = dt.datetime(2026, 10, 20, 9), dt.datetime(2026, 10, 31, 23, 59, 59)


def d2_person(rng, who_b, what_b):
    what = [w for w in D2_WHAT if rng.random() < (0.7 if w == what_b else 0.3)] or [what_b]
    return [rng.choice(NICK), rng.choice(COUNTRIES[1:]), who_b if rng.random() < 0.45 else rng.choice(D2_WHO),
            ", ".join(what), str(rng.choice([1, 1, 2, 2, 3, 3, 4, 5])), rng.choice(WISH)]


def d2(no):
    base = random.Random(SALT * 20 + no)
    who_t, what_t = D2_WHO[(no - 1) % 4], D2_WHAT[(no - 1) % 5]
    who_x, what_x = D2_WHO[(no + 1) % 4], D2_WHAT[(no + 2) % 5]
    for _ in range(20000):
        rng = random.Random(base.random())
        n = rng.randint(20, 26)
        people = [[ts_between(rng, D2_OPEN + dt.timedelta(hours=8), D2_CLOSE), f"u{i + 1:03d}@example.com",
                   d2_person(rng, who_t, what_t)] for i in range(n)]
        rows = [(p[0], p[1], p[2]) for p in people]
        for p in rng.sample(people, 2):  # 罠: 重複（古い行）
            old = d2_person(rng, who_x, what_x)
            old[0] = p[2][0]
            rows.append((p[0] - dt.timedelta(hours=rng.randrange(1, 8)), p[1], old))
        for j in range(2):  # 罠: テスト送信
            rows.append((dt.datetime(2026, 10, 19, 18, 10 + j * 3), STAFF, ["テスト", "その他", who_x, what_x, "1", ""]))
        rows.sort(key=lambda r: r[0])
        valid = [p[2] for p in people]
        raw = [r[2] for r in rows]

        def tally(group):
            who = {w: sum(g[2] == w for g in group) for w in D2_WHO}
            what = {w: sum(w in split(g[3]) for g in group) for w in D2_WHAT}
            low = sum(g[4] in ("1", "2") for g in group)
            return who, what, low
        who, what, low = tally(valid)
        rwho, rwhat, rlow = tally(raw)
        W, H = top1(who), top1(what)
        if W != who_t or H != what_t:
            continue
        flips = (top1(rwho) not in (None, W)) + (top1(rwhat) not in (None, H))
        if flips >= 1 and rhu(low / n * 100) != rhu(rlow / len(raw) * 100):
            break
    else:
        raise RuntimeError(no)
    date = dt.date(2026, 12, 5) if no % 2 else dt.date(2026, 12, 6)
    out = [[r[0].strftime("%Y/%m/%d %H:%M:%S"), r[1]] + r[2] for r in rows]
    key = {"番号": f"{no:02d}", "B1_有効回答": n, "B2_相手": W, "B3_困りごと": H, "B4_人数": what[H],
           "B5_自信1か2": low, "B6_割合%": int(rhu(low / n * 100)),
           "3枚目_日時": f"{fd(date)} 14:00〜15:30", "3枚目_締切": fd(date - dt.timedelta(days=3)),
           "誤_掃除なしB1": len(raw), "誤_掃除なし相手": top1(rwho) or "同数", "誤_掃除なし困りごと": top1(rwhat) or "同数",
           "誤_掃除なし割合%": int(rhu(rlow / len(raw) * 100))}
    return out, key


# ================= d3・d4 共通: ターゲットを絞る調査 =================
def survey(no, cfg):
    base = random.Random(SALT * cfg["salt"] + no)
    scene_t, scene_a = cfg["scenes"][(no - 1) % 4], cfg["scenes"][(no + 1) % 4]
    slots = [(d, t) for d in cfg["days"] for t in cfg["times"]]
    slot_t, slot_a = slots[(no * 2) % len(slots)], slots[(no * 2 + len(slots) // 2) % len(slots)]
    slot_2 = None
    if cfg.get("competitor"):  # 最多の時間と2番目の時間を番号で決める（競合ルールの答えが偏らないように）
        pick = [("平日", "昼"), ("土日", "夜")][no % 2]
        top = [pick, pick, ("土日", "昼"), ("平日", "夜")][no % 4]
        slot_t, slot_2 = top, (None if top == pick else pick)
        slot_a = next(x for x in slots if x not in (slot_t, slot_2))
    sns_t = cfg["carousel_sns"][(no - 1) % len(cfg["carousel_sns"])] if cfg.get("carousel_sns") else None
    hour_t = [21, 22, 12, 20, 23, 7][(no - 1) % 6]
    for _ in range(20000):
        rng = random.Random(base.random())
        n_unique = rng.randint(*cfg["n_unique"])

        def person(attended, sbias, slbias, snsbias, hbias, star_trap, slbias2=None):
            a = {"nick": rng.choice(NICK), "att": "はい" if attended else "いいえ",
                 "country": rng.choice(COUNTRIES[1:])}
            a["sns"] = ", ".join([s for s in cfg["sns"] if rng.random() < {"LINE": 0.9, "YouTube": 0.45}.get(s, 0.25)
                                  + (0.45 if s == snsbias else 0)] or ["LINE"])
            for sc in cfg["scenes"]:
                p = 0.62 if sc == sbias else 0.22
                r = rng.random()
                a["q5_" + sc] = "よく困る" if r < p else ("ときどき困る" if r < p + 0.4 * (1 - p) else "困らない")
            for d in cfg["days"]:
                a["q6_" + d] = ", ".join(t for t in cfg["times"] if rng.random() < (
                    0.72 if (d, t) == slbias else 0.5 if (d, t) == slbias2 else 0.2))
            a["scale"] = str(rng.choice([1, 2, 2, 3, 3, 4, 5]))
            a["star"] = str(rng.choice([3, 4, 4, 4, 5, 5])) if attended else (
                str(rng.choice([1, 2, 2, 3])) if rng.random() < star_trap else "")
            a["date"] = (cfg["date_from"] + dt.timedelta(rng.randrange(0, 20))).strftime("%Y/%m/%d")
            h = hbias if rng.random() < 0.45 else rng.choice([7, 8, 12, 18, 20, 21, 22, 23])
            a["time"] = f"{h}:{rng.randrange(60):02d}:00"
            a["wish"] = rng.choice(WISH)
            return a

        people = []
        for i in range(n_unique):
            att = rng.random() < 0.4
            a = (person(True, scene_a, slot_a, rng.choice(["LINE", "YouTube"]), rng.choice([8, 18]), 0) if att
                 else person(False, scene_t, slot_t, sns_t, hour_t, 0.35, slot_2))
            people.append([ts_between(rng, cfg["open"], cfg["close"]), f"u{i + 1:03d}@example.com", a])
        for p in rng.sample(people, rng.choice([2, 3])):
            p[2]["country"] = "日本"
        recs = [tuple(p) for p in people]
        for j in range(2):  # 締切後
            recs.append((cfg["close"] + dt.timedelta(hours=rng.randrange(1, 10)), f"u{n_unique + j + 1:03d}@example.com",
                         person(False, scene_a, slot_a, "LINE", hour_t, 0.5)))
        cand = [p for p in people if p[2]["country"] != "日本" and p[0] > cfg["open"] + dt.timedelta(hours=6)]
        for p in rng.sample(cand, 3):  # 重複（古い行は「いいえ」）
            a = person(False, scene_a, slot_a, "LINE", hour_t, 0.8)
            a["nick"] = p[2]["nick"]
            gap = min(48, int((p[0] - cfg["open"]).total_seconds() // 3600))
            recs.append((p[0] - dt.timedelta(hours=rng.randrange(2, gap)), p[1], a))
        for j in range(2):  # テスト送信
            a = person(bool(j), scene_a, slot_a, "LINE", 9, 1)
            a["nick"], a["country"] = "テスト", "その他"
            recs.append((cfg["open"] - dt.timedelta(hours=15, minutes=j * 7), STAFF, a))
        recs.sort(key=lambda r: r[0])
        rows = [cfg["row"](r) for r in recs]
        k = analyze(rows, cfg)
        if k is None:
            continue
        ok = (k["scene"] == scene_t and k["scene_all"] not in (None, scene_t) and k["slot"] == slot_t
              and k["slot_all"] not in (None, slot_t) and k["star"] != k["star_all"] and k["star"] != k["star_raw"]
              and k["n_tgt"] != k["n_tgt_raw"] and k["n_tgt"] >= 15 and len(k["stars"]) >= 5)
        if cfg.get("carousel_sns"):
            ok = ok and k["sns"] == sns_t and k["line"] > k["sns_n"]
        if cfg.get("q_time"):
            ok = ok and k["hour"] == hour_t
        if cfg.get("competitor"):  # 4つの時間の人数がすべて違う（順位が1通りに決まる）
            ok = ok and len(set(k["sl"].values())) == len(k["sl"])
            if slot_2:
                ok = ok and sorted(k["sl"], key=lambda x: -k["sl"][x])[1] == "".join(slot_2)
        if ok:
            return rows, k
    raise RuntimeError(no)


def analyze(rows, cfg, clean=True):
    H = cfg["header"]
    ix = {h: i for i, h in enumerate(H)}
    last = {}
    for i, r in enumerate(rows):
        last[r[1]] = i
    valid, excl = [], []
    for i, r in enumerate(rows):
        bad = (r[1] == STAFF or dt.datetime.strptime(r[0], "%Y/%m/%d %H:%M:%S") > cfg["close"]
               or last[r[1]] != i or r[ix[cfg["q_country"]]] == "日本")
        if clean and bad:
            excl.append(i + 2)
        else:
            valid.append(r)

    def res(group_valid):
        tgt = [r for r in group_valid if r[ix[cfg["q_att"]]] == "いいえ"]
        att = [r for r in group_valid if r[ix[cfg["q_att"]]] == "はい"]
        sc = {s: sum(r[ix[f"{cfg['q_scene']} [{s}]"]] == "よく困る" for r in tgt) for s in cfg["scenes"]}
        sc_all = {s: sum(r[ix[f"{cfg['q_scene']} [{s}]"]] == "よく困る" for r in group_valid) for s in cfg["scenes"]}
        sl = {d + t: sum(t in split(r[ix[f"{cfg['q_slot']} [{d}]"]]) for r in tgt) for d in cfg["days"] for t in cfg["times"]}
        sl_all = {d + t: sum(t in split(r[ix[f"{cfg['q_slot']} [{d}]"]]) for r in group_valid)
                  for d in cfg["days"] for t in cfg["times"]}
        stars = [int(r[ix[cfg["q_star"]]]) for r in att if r[ix[cfg["q_star"]]]]
        stars_all = [int(r[ix[cfg["q_star"]]]) for r in group_valid if r[ix[cfg["q_star"]]]]
        return tgt, sc, sc_all, sl, sl_all, stars, stars_all
    tgt, sc, sc_all, sl, sl_all, stars, stars_all = res(valid)
    rtgt, _, _, _, _, _, rstars_all = res(rows)
    if not stars or not stars_all:
        return None
    k = {"n_valid": len(valid), "n_tgt": len(tgt), "n_tgt_raw": len(rtgt), "n_raw": len(rows),
         "scene": top1(sc), "scene_all": top1(sc_all), "sc": sc, "slot_t": None,
         "slot": None, "slot_all": None, "sl": sl, "stars": stars,
         "star": rhu(sum(stars) / len(stars), 1), "star_all": rhu(sum(stars_all) / len(stars_all), 1),
         "star_raw": rhu(sum(rstars_all) / len(rstars_all), 1), "excl": excl}
    s1, s2 = top1(sl), top1(sl_all)
    k["slot"] = tuple(next((d, t) for d in cfg["days"] for t in cfg["times"] if d + t == s1)) if s1 else None
    k["slot_all"] = tuple(next((d, t) for d in cfg["days"] for t in cfg["times"] if d + t == s2)) if s2 else None
    if k["scene"] is None or k["slot"] is None:
        return None
    if cfg.get("carousel_sns"):
        cnt = {s: sum(s in split(r[ix[cfg["q_sns"]]]) for r in tgt) for s in cfg["sns"]}
        k["sns"] = top1({s: cnt[s] for s in cfg["carousel_sns"]})
        k["sns_n"] = cnt.get(k["sns"], 0)
        k["line"] = cnt["LINE"]
        if k["sns"] is None:
            return None
    if cfg.get("q_time"):
        hours = {}
        for r in tgt:
            h = int(r[ix[cfg["q_time"]]].split(":")[0])
            hours[h] = hours.get(h, 0) + 1
        k["hour"] = top1(hours)
        if k["hour"] is None:
            return None
    return k


# ---- d3: 日本語講座の希望調査（9問） ----
D3 = dict(salt=30, competitor=True, scenes=["敬語", "漢字", "聞き取り", "電話"], days=["平日", "土日"], times=["昼", "夜"],
          sns=["Instagram", "TikTok", "Facebook", "X", "YouTube", "LINE"], n_unique=(32, 38),
          open=dt.datetime(2026, 11, 2, 9), close=dt.datetime(2026, 11, 15, 23, 59, 59), date_from=dt.date(2026, 12, 1),
          q_att="日本語講座に来たことがありますか", q_country="出身の国・地域を選んでください",
          q_scene="次のことで困りますか", q_slot="参加しやすい時間をすべて選んでください",
          q_star="前回の講座の満足度を星で教えてください（来たことがある人だけ）", q_sns="ふだん使うSNSをすべて選んでください")
D3["header"] = (["タイムスタンプ", "メールアドレス", "ニックネームを書いてください", D3["q_att"], D3["q_country"], D3["q_sns"]]
                + [f"{D3['q_scene']} [{s}]" for s in D3["scenes"]] + [f"{D3['q_slot']} [{d}]" for d in D3["days"]]
                + ["日本語で話す自信はどのくらいですか", D3["q_star"], "講座でやってみたいことを自由に書いてください"])
D3["row"] = lambda r: ([r[0].strftime("%Y/%m/%d %H:%M:%S"), r[1], r[2]["nick"], r[2]["att"], r[2]["country"], r[2]["sns"]]
                       + [r[2]["q5_" + s] for s in D3["scenes"]] + [r[2]["q6_" + d] for d in D3["days"]]
                       + [r[2]["scale"], r[2]["star"], r[2]["wish"]])
D3_DATES = {("平日", "昼"): (dt.date(2026, 12, 9), "13:00〜14:30"), ("平日", "夜"): (dt.date(2026, 12, 10), "19:00〜20:30"),
            ("土日", "昼"): (dt.date(2026, 12, 12), "13:00〜14:30"), ("土日", "夜"): (dt.date(2026, 12, 13), "18:00〜19:30")}

# ---- d4: アルバイトの日本語講座（11問） ----
D4 = dict(salt=40, scenes=["面接", "電話", "接客", "シフトの相談"], days=["平日", "土曜", "日曜"], times=["午前", "午後", "夜"],
          sns=["Instagram", "TikTok", "Facebook", "YouTube", "LINE"],
          n_unique=(36, 42), open=dt.datetime(2026, 12, 1, 9), close=dt.datetime(2026, 12, 14, 23, 59, 59),
          date_from=dt.date(2027, 2, 1),
          q_att="アルバイトの日本語講座に来たことがありますか", q_country="出身の国・地域を選んでください",
          q_scene="アルバイトの次の場面で、日本語に困りますか", q_slot="参加しやすい時間をすべて選んでください",
          q_star="前回の講座の満足度を星で教えてください（来たことがある人だけ）", q_sns="ふだん使うSNSをすべて選んでください",
          q_time="SNSをいちばんよく見る時刻を教えてください")
D4["header"] = (["タイムスタンプ", "メールアドレス", "ニックネームを書いてください", D4["q_att"], D4["q_country"], D4["q_sns"]]
                + [f"{D4['q_scene']} [{s}]" for s in D4["scenes"]] + [f"{D4['q_slot']} [{d}]" for d in D4["days"]]
                + ["日本語で話す自信はどのくらいですか", D4["q_star"], "次に来られそうな日を選んでください", D4["q_time"],
                   "講座でやってみたいことを自由に書いてください"])
D4["row"] = lambda r: ([r[0].strftime("%Y/%m/%d %H:%M:%S"), r[1], r[2]["nick"], r[2]["att"], r[2]["country"], r[2]["sns"]]
                       + [r[2]["q5_" + s] for s in D4["scenes"]] + [r[2]["q6_" + d] for d in D4["days"]]
                       + [r[2]["scale"], r[2]["star"], r[2]["date"], r[2]["time"], r[2]["wish"]])
# 2027年2月の会場の予定（✖＝使えない）。祝日は「休館」と表に書く（祝日の扱いは最終課題で初めて問う）
D4_CLOSED = {dt.date(2027, 2, 11), dt.date(2027, 2, 23)}
D4_NG = ({(dt.date(2027, 2, d), "夜") for d in range(1, 6)} | {(dt.date(2027, 2, d), "午前") for d in (1, 2, 3)}
         | {(dt.date(2027, 2, 6), "午前"), (dt.date(2027, 2, 6), "夜"), (dt.date(2027, 2, 7), "午後"), (dt.date(2027, 2, 7), "夜")})
D4_TIME = {"午前": "10:00〜11:30", "午後": "14:00〜15:30", "夜": "19:00〜20:30"}


def d4_first(slot):
    d0 = dt.date(2027, 2, 1)
    for i in range(28):
        d = d0 + dt.timedelta(i)
        if d in D4_CLOSED or (d, slot[1]) in D4_NG:
            continue
        typ = "土曜" if d.weekday() == 5 else "日曜" if d.weekday() == 6 else "平日"
        if typ == slot[0]:
            return d
    raise ValueError(slot)


# 材料D（Googleマップの写し・架空）: 強い競合＝評価4.0以上かつ口コミ20件以上
D3_COMPETITORS = [("あおば日本語教室", 4.9, 3, "土日夜"), ("さくら日本語スクール", 4.3, 41, "土日昼"),
                  ("みなと語学センター", 3.6, 58, "平日昼"), ("ひまわり日本語サロン", 4.1, 12, "平日昼"),
                  ("つばめ日本語クラブ", 4.0, 20, "平日夜")]


def d3_pick(sl, strong_rule):
    strong = {c[3] for c in D3_COMPETITORS if strong_rule(c)}
    order = sorted(sl, key=lambda x: -sl[x])
    return next((x for x in order if x not in strong), "どこも開けない")


def d3(no):
    rows, k = survey(no, D3)
    sl = k["sl"]
    pick = d3_pick(sl, lambda c: c[1] >= 4.0 and c[2] >= 20)
    k["slot"] = next((d, t) for d in D3["days"] for t in D3["times"] if d + t == pick)
    date, time = D3_DATES[k["slot"]]
    key = {"番号": f"{no:02d}", "B1_有効回答": k["n_valid"], "B2_ターゲット": k["n_tgt"], "B3_苦手": k["scene"],
           "B4_よく困る人数": k["sc"][k["scene"]], "B5_割合%": int(rhu(k["sc"][k["scene"]] / k["n_tgt"] * 100)),
           "B6_時間帯": "".join(k["slot"]), "B7_選んだ人数": k["sl"]["".join(k["slot"])],
           "B8_満足度": str(k["star"]), "B9_満足度の人数": len(k["stars"]),
           "B10_最初の回": f"{fd(date)} {time}", "B11_申込締切": fd(date - dt.timedelta(days=3)),
           "除外した行": " ".join(map(str, k["excl"])),
           "誤_掃除なしB1": k["n_raw"], "誤_掃除なしB2": k["n_tgt_raw"], "誤_全員で数えた苦手": k["scene_all"],
           "誤_全員で数えた時間帯": "".join(k["slot_all"]), "誤_いいえの星も入れた満足度": str(k["star_all"]),
           "誤_掃除なし満足度": str(k["star_raw"]),
           "誤_競合を見ない時間帯": max(sl, key=sl.get),
           "誤_口コミ3件も強いとした時間帯": d3_pick(sl, lambda c: c[1] >= 4.0),
           "誤_4.0と20件を外した時間帯": d3_pick(sl, lambda c: c[1] > 4.0 and c[2] > 20)}
    return rows, key


# 材料（GA4 の写し・架空）: 番号ごとに、カフェのサイトに SNS から来たユーザー数とセッション数
GA4_SRC = ["instagram.com", "tiktok.com", "facebook.com", "line.me", "youtube.com"]
GA4_NAME = {"instagram.com": "Instagram", "tiktok.com": "TikTok", "facebook.com": "Facebook"}


def ga4(no):
    rng = random.Random(SALT * 50 + no)
    car = ["instagram.com", "tiktok.com", "facebook.com"]
    u_top, s_top = car[(no - 1) % 3], car[no % 3]
    third = next(c for c in car if c not in (u_top, s_top))
    U = rng.randint(180, 320)
    users = {u_top: U, s_top: U - rng.randint(8, 40), third: U - rng.randint(60, 120),
             "line.me": U + rng.randint(30, 90), "youtube.com": rng.randint(40, 90)}
    sess = {u_top: int(users[u_top] * rng.uniform(1.15, 1.35)), s_top: int(users[s_top] * rng.uniform(1.9, 2.4)),
            third: int(users[third] * rng.uniform(1.2, 1.6)), "line.me": int(users["line.me"] * rng.uniform(1.3, 1.6)),
            "youtube.com": int(users["youtube.com"] * rng.uniform(1.1, 1.3))}
    assert sess[s_top] > sess[u_top] and users["line.me"] > users[u_top] > users[s_top] > users[third]
    rows = [[f"{src} / referral", users[src], sess[src], f"{rng.uniform(45, 75):.1f}%"] for src in GA4_SRC]
    rows.sort(key=lambda r: -r[2])  # GA4 の初期表示のように、セッションの多い順に並べる
    return rows, GA4_NAME[u_top], GA4_NAME[s_top]


def d4(no):
    rows, k = survey(no, D4)
    date = d4_first(k["slot"])
    g_rows, g_user, g_sess = ga4(no)
    os.makedirs(os.path.join(HERE, "d4", "data"), exist_ok=True)
    with open(os.path.join(HERE, "d4", "data", f"ga4-{no:02d}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["セッションの参照元 / メディア", "ユーザー", "セッション", "エンゲージメント率"])
        w.writerows(g_rows)
    key = {"番号": f"{no:02d}", "B1_有効回答": k["n_valid"], "B2_ターゲット": k["n_tgt"], "B3_場面": k["scene"],
           "B4_よく困る人数": k["sc"][k["scene"]], "B5_割合%": int(rhu(k["sc"][k["scene"]] / k["n_tgt"] * 100)),
           "B6_投稿先": g_user, "B7_投稿時間帯": f"{k['hour']}時台",
           "B8_曜日時間帯": "".join(k["slot"]), "B9_選んだ人数": k["sl"]["".join(k["slot"])],
           "B10_満足度": str(k["star"]), "B11_満足度の人数": len(k["stars"]),
           "B12_最初の回": f"{fd(date)} {D4_TIME[k['slot'][1]]}", "B13_申込締切": fd(date - dt.timedelta(days=4)),
           "除外した行": " ".join(map(str, k["excl"])),
           "誤_掃除なしB1": k["n_raw"], "誤_掃除なしB2": k["n_tgt_raw"], "誤_全員で数えた場面": k["scene_all"],
           "グラフ_ターゲットのよく困る人数": " ".join(f"{s}{k['sc'][s]}" for s in D4["scenes"]),
           "誤_全員で数えた時間帯": "".join(k["slot_all"]), "誤_LINEを含めた投稿先": "LINE",
           "誤_セッションで選んだ投稿先": g_sess,
           "誤_いいえの星も入れた満足度": str(k["star_all"]), "誤_掃除なし満足度": str(k["star_raw"])}
    return rows, key


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    for level, fn, header in [("d1", d1, ["タイムスタンプ", "メールアドレス"] + D1_Q),
                              ("d2", d2, ["タイムスタンプ", "メールアドレス"] + D2_Q),
                              ("d3", d3, D3["header"]), ("d4", d4, D4["header"])]:
        rows_by_no, keys = {}, []
        for no in range(1, n + 1):
            rows, key = fn(no)
            rows_by_no[no] = rows
            keys.append(key)
        write(level, header, rows_by_no, keys)
        print(level, "作成", n, "人分")


if __name__ == "__main__":
    main()
