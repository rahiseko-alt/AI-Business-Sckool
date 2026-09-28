# -*- coding: utf-8 -*-
"""d1〜d4 の正解表を、make_practice.py とは別の書き方で数え直して照合する。
python3 verify_practice.py          → 全部を照合
python3 verify_practice.py d3 07    → d3 の07番の正解を表示（採点用）
"""
import csv
import os
import sys
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
WD = "月火水木金土日"
STAFF = "cafe-staff@example.com"


def jd(d):
    return f"{d.month}月{d.day}日（{WD[d.weekday()]}）"


def pct(a, b):
    return str(int((Decimal(a) * 100 / Decimal(b)).quantize(Decimal(1), ROUND_HALF_UP)))


def avg1(xs):
    return str((Decimal(sum(xs)) / len(xs)).quantize(Decimal("0.1"), ROUND_HALF_UP))


def load(level, no):
    with open(os.path.join(HERE, level, "data", f"responses-{no}.csv"), encoding="utf-8") as f:
        rd = list(csv.reader(f))
    return rd[0], rd[1:]


def col(head, prefix):
    return [i for i, h in enumerate(head) if h.startswith(prefix)]


def only_top(c):
    (a, x), (_, y) = c.most_common(2)
    assert x > y, c
    return a, x


def clean(head, body, close=None, country=True):
    last = {r[1]: i for i, r in enumerate(body)}
    ci = col(head, "出身")
    keep = []
    for i, r in enumerate(body):
        if r[1] == STAFF or last[r[1]] != i:
            continue
        if close and r[0] > close:
            continue
        if country and ci and r[ci[0]] == "日本":
            continue
        keep.append(r)
    return keep


def v_d1(no):
    head, body = load("d1", no)
    keep = [r for r in body if r[1] != STAFF]
    c = Counter(x for r in keep for x in r[4].split(", "))
    t, n = only_top(c)
    return {"B1_有効回答": str(len(keep)), "B2_知りたい日本語": t, "B3_人数": str(n)}


def v_d2(no):
    head, body = load("d2", no)
    keep = clean(head, body, country=False)
    who, _ = only_top(Counter(r[4] for r in keep))
    what, k = only_top(Counter(x for r in keep for x in r[5].split(", ")))
    low = sum(1 for r in keep if int(r[6]) <= 2)
    d = date(2026, 12, 5) if int(no) % 2 else date(2026, 12, 6)
    return {"B1_有効回答": str(len(keep)), "B2_相手": who, "B3_困りごと": what, "B4_人数": str(k),
            "B5_自信1か2": str(low), "B6_割合%": pct(low, len(keep)),
            "3枚目_日時": f"{jd(d)} 14:00〜15:30", "3枚目_締切": jd(d - timedelta(3))}


def survey(level, no, close, scene_q, slot_q):
    head, body = load(level, no)
    keep = clean(head, body, close=close)
    tgt = [r for r in keep if r[3] == "いいえ"]
    sc = Counter()
    for i in col(head, scene_q):
        sc[head[i].split("[")[1][:-1]] = sum(r[i] == "よく困る" for r in tgt)
    s, sn = only_top(sc)
    sl = Counter()
    for i in col(head, slot_q):
        for r in tgt:
            for t in r[i].split(", "):
                if t:
                    sl[head[i].split("[")[1][:-1] + t] += 1
    slot, sln = only_top(sl)
    si = col(head, "前回の講座の満足度")[0]
    stars = [int(r[si]) for r in keep if r[3] == "はい" and r[si]]
    return head, keep, tgt, s, sn, slot, sln, stars


def v_d3(no):
    head, keep, tgt, s, sn, slot, sln, stars = survey("d3", no, "2026/11/15 23:59:59", "次のことで困りますか", "参加しやすい時間")
    table = {"平日昼": (date(2026, 12, 9), "13:00〜14:30"), "平日夜": (date(2026, 12, 10), "19:00〜20:30"),
             "土日昼": (date(2026, 12, 12), "13:00〜14:30"), "土日夜": (date(2026, 12, 13), "18:00〜19:30")}
    d, tm = table[slot]
    return {"B1_有効回答": str(len(keep)), "B2_ターゲット": str(len(tgt)), "B3_苦手": s, "B4_よく困る人数": str(sn),
            "B5_割合%": pct(sn, len(tgt)), "B6_時間帯": slot, "B7_選んだ人数": str(sln), "B8_満足度": avg1(stars),
            "B9_満足度の人数": str(len(stars)), "B10_最初の回": f"{jd(d)} {tm}", "B11_申込締切": jd(d - timedelta(3))}


# d4/00_課題と材料.md の会場予定の表から、○の日だけを手で写したもの（最初の数日）
D4_OK = {"平日午前": ["2/4", "2/5"], "平日午後": ["2/1", "2/2"], "平日夜": ["2/8", "2/9"],
         "土曜午前": ["2/13"], "土曜午後": ["2/6"], "土曜夜": ["2/13"],
         "日曜午前": ["2/7"], "日曜午後": ["2/14"], "日曜夜": ["2/14"]}


def v_d4(no):
    head, keep, tgt, s, sn, slot, sln, stars = survey("d4", no, "2026/12/14 23:59:59", "アルバイトの次の場面", "参加しやすい時間")
    si = col(head, "ふだん使うSNS")[0]
    sns, _ = only_top(Counter(x for r in tgt for x in r[si].split(", ") if x in ("Instagram", "TikTok", "Facebook")))
    ti = col(head, "SNSをいちばんよく見る時刻")[0]
    hr, _ = only_top(Counter(r[ti].split(":")[0] for r in tgt))
    m, dd = map(int, D4_OK[slot][0].split("/"))
    d = date(2027, m, dd)
    tm = {"午前": "10:00〜11:30", "午後": "14:00〜15:30", "夜": "19:00〜20:30"}[slot[2:]]
    return {"B1_有効回答": str(len(keep)), "B2_ターゲット": str(len(tgt)), "B3_場面": s, "B4_よく困る人数": str(sn),
            "B5_割合%": pct(sn, len(tgt)), "B6_投稿先": sns, "B7_投稿時間帯": f"{hr}時台", "B8_曜日時間帯": slot,
            "B9_選んだ人数": str(sln), "B10_満足度": avg1(stars), "B11_満足度の人数": str(len(stars)),
            "B12_最初の回": f"{jd(d)} {tm}", "B13_申込締切": jd(d - timedelta(4))}


def main():
    fns = {"d1": v_d1, "d2": v_d2, "d3": v_d3, "d4": v_d4}
    if len(sys.argv) == 3:
        level, no = sys.argv[1], sys.argv[2].zfill(2)
        with open(os.path.join(HERE, level, "05_正解表_教員用.csv"), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["番号"] == no:
                    for k, v in r.items():
                        print(f"{k}: {v}")
        return
    for level, fn in fns.items():
        with open(os.path.join(HERE, level, "05_正解表_教員用.csv"), encoding="utf-8") as f:
            keys = list(csv.DictReader(f))
        for k in keys:
            mine = fn(k["番号"])
            for field, v in mine.items():
                assert k[field] == v, (level, k["番号"], field, k[field], v)
        print(level, len(keys), "人分、正解表と独立の数え直しが一致")


if __name__ == "__main__":
    main()
