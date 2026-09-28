# -*- coding: utf-8 -*-
"""正解表（05_正解表_教員用.csv）を、make_versions.py とは別の書き方で数え直して照合する。
学生の提出を採点するときにも、番号を渡せばその番号の正解を表示する: python3 verify.py 07
"""
import csv
import os
import sys
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
WD = "月火水木金土日"

# 04_会場の予定.md の表を、ここでは「○の日の一覧」として書き直したもの（手で写した）
OK_DAYS = {
    "平日午前": ["1/7", "1/8", "1/11", "1/12"], "平日午後": ["1/5", "1/6"], "平日夜": ["1/11", "1/12"],
    "土曜午前": ["1/16"], "土曜午後": ["1/9"], "土曜夜": ["1/16"],
    "日曜午前": ["1/10"], "日曜午後": ["1/17"], "日曜夜": ["1/17"],
}
HOLIDAY = "1/11"
TIME = {"午前": "10:00〜11:30", "午後": "14:00〜15:30", "夜": "19:00〜20:30"}


def jp(md):
    m, d = map(int, md.split("/"))
    x = date(2027, m, d)
    return x, f"{m}月{d}日（{WD[x.weekday()]}）"


def recount(no):
    with open(os.path.join(HERE, "data", f"responses-{no}.csv"), encoding="utf-8") as f:
        rd = list(csv.reader(f))
    head, body = rd[0], rd[1:]
    col = {h: i for i, h in enumerate(head)}
    last = {}
    for i, r in enumerate(body):
        last[r[1]] = i
    keep, drop = [], []
    for i, r in enumerate(body):
        bad = (r[1] == "cafe-staff@example.com" or r[0] > "2026/11/30 23:59:59"
               or last[r[1]] != i or r[4] == "日本")
        (drop if bad else keep).append((i + 2, r))
    tgt = [r for _, r in keep if r[3] == "いいえ"]
    scene = Counter()
    for r in tgt:
        for h in head:
            if h.startswith("次の場面で") and r[col[h]] == "よく困る":
                scene[h.split("[")[1].rstrip("]")] += 1
    (s, sc), (_, sc2) = scene.most_common(2)
    assert sc > sc2
    slot = Counter()
    for r in tgt:
        for h in head:
            if h.startswith("参加しやすい時間"):
                for t in r[col[h]].split(", "):
                    if t:
                        slot[h.split("[")[1].rstrip("]") + t] += 1
    (sl, slc), (_, slc2) = slot.most_common(2)
    assert slc > slc2
    sns = Counter(x for r in tgt for x in r[5].split(", ") if x in ("Instagram", "TikTok", "Facebook"))
    (sn, n1), (_, n2) = sns.most_common(2)
    assert n1 > n2
    hours = Counter(int(r[col["SNSをいちばんよく見る時刻を教えてください"]].split(":")[0]) for r in tgt)
    (hr, h1), (_, h2) = hours.most_common(2)
    assert h1 > h2
    stars = [int(r[14]) for _, r in keep if r[3] == "はい" and r[14]]
    avg = Decimal(sum(stars)) / Decimal(len(stars))
    days = [d for d in OK_DAYS[sl] if not (sl.startswith("平日") and d == HOLIDAY)]
    first, first_s = jp(days[0])
    _, dl = jp(f"{(first - timedelta(3)).month}/{(first - timedelta(3)).day}")
    return {
        "B1_有効回答": str(len(keep)), "B2_ターゲット": str(len(tgt)), "B3_場面": s, "B4_よく困る人数": str(sc),
        "B5_割合%": str(int((Decimal(sc) * 100 / len(tgt)).quantize(Decimal(1), ROUND_HALF_UP))),
        "B6_投稿先": sn, "B7_投稿時間帯": f"{hr}時台", "B8_曜日時間帯": sl, "B9_選んだ人数": str(slc),
        "B10_満足度": str(avg.quantize(Decimal("0.1"), ROUND_HALF_UP)), "B11_満足度の人数": str(len(stars)),
        "B12_最初の回": f"{first_s} {TIME[sl[2:]]}", "B13_申込締切": dl,
        "B14_除外した行": " ".join(str(n) for n, _ in drop),
    }


def main():
    with open(os.path.join(HERE, "05_正解表_教員用.csv"), encoding="utf-8") as f:
        keys = {r["番号"]: r for r in csv.DictReader(f)}
    if len(sys.argv) > 1:
        no = sys.argv[1].zfill(2)
        for k, v in keys[no].items():
            print(f"{k}: {v}")
        return
    for no, k in keys.items():
        mine = recount(no)
        for field, v in mine.items():
            assert k[field] == v, (no, field, k[field], v)
    print(f"{len(keys)}人分、正解表と独立の数え直しが一致")


if __name__ == "__main__":
    main()
