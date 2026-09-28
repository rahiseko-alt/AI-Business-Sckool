# -*- coding: utf-8 -*-
"""成果物1: 番号版の事実カードと正解表を作り、検算する。 python3 make_versions.py [人数]"""
import csv
import datetime as dt
import os
import random
import sys

SALT = 2026
HERE = os.path.dirname(os.path.abspath(__file__))
WD = "月火水木金土日"
PLACES = ["みなと市民センター 2階 会議室A", "みなと市民センター 2階 会議室B", "みなと市民センター 3階 和室",
          "みなと図書館 1階 集会室", "みなと公民館 2階 学習室"]
TIMES = ["10:00〜11:30", "13:00〜14:30", "14:00〜15:30", "15:30〜17:00", "18:30〜20:00"]


def fd(d):
    return f"{d.month}月{d.day}日（{WD[d.weekday()]}）"


def make(no):
    rng = random.Random(SALT * 1000 + no)
    sats = [dt.date(2026, 11, 1) + dt.timedelta(i) for i in range(30)]
    sats = [d for d in sats if d.weekday() in (5, 6)]
    date0 = rng.choice(sats[:-2])
    time0 = rng.choice(TIMES)
    place0 = rng.choice(PLACES)
    cap = rng.randrange(12, 31)
    n = rng.randrange(14, 29)            # 去年の参加者
    m = rng.randrange(n // 2 + 1, n)     # 役に立ったと答えた人
    kind = ["日付", "時間", "場所"][(no - 1) % 3]
    date1, time1, place1 = date0, time0, place0
    if kind == "日付":
        date1 = date0 + dt.timedelta(days=7)
    elif kind == "時間":
        time1 = rng.choice([t for t in TIMES if t != time0])
    else:
        place1 = rng.choice([p for p in PLACES if p != place0])
    card = {
        "番号": f"{no:02d}", "開催日_カード": fd(date0), "時間_カード": time0, "場所_カード": place0,
        "定員": cap, "去年の参加者": n, "役に立った": m, "訂正": kind,
        "開催日_正": fd(date1), "時間_正": time1, "場所_正": place1,
        "締切_正": fd(date1 - dt.timedelta(days=2)),
        "誤_訂正前の締切": fd(date0 - dt.timedelta(days=2)),
        "割合_参考": f"{round(m / n * 100)}%（材料にないので書けば✖）",
    }
    return card


def card_md(c):
    fix = {"日付": f"開催日は **{c['開催日_正']}** に変わりました",
           "時間": f"時間は **{c['時間_正']}** に変わりました",
           "場所": f"場所は **{c['場所_正']}** に変わりました"}[c["訂正"]]
    return f"""## 事実カード {c['番号']}

- 催し: 防災の日本語ワークショップ（みなと日本語カフェ・架空）
- 読む人: 日本に来て1年目の留学生
- してほしい行動: 申込フォームから申し込む
- 開催日: {c['開催日_カード']}
- 時間: {c['時間_カード']}
- 場所: {c['場所_カード']}
- 定員: {c['定員']}人（先着順） ／ 参加費: 0円 ／ 持ち物: スマホ
- 申込: カフェのプロフィールのリンクの申込フォーム。締切は開催日の2日前
- 内容: 地震のときに使う日本語（「逃げて」「ここは安全です」など）を、声に出して練習する
- 去年の同じワークショップ: 参加者{c['去年の参加者']}人のうち{c['役に立った']}人が、アンケートで「役に立った」と答えた
- カフェの別のイベント（料理の会）の満足度: 95%（回答20人）

> 訂正（カフェのスタッフより）: {fix}。ほかは変わりません。
"""


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    cards = [make(i) for i in range(1, n + 1)]
    with open(os.path.join(HERE, "01_事実カード.md"), "w", encoding="utf-8") as f:
        f.write("# 成果物1 事実カード（1人1枚。自分の番号だけを渡す）\n\n")
        f.write("\n".join(card_md(c) for c in cards))
    with open(os.path.join(HERE, "05_正解表_教員用.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(cards[0].keys()))
        w.writeheader()
        w.writerows(cards)
    # 検算: 締切は訂正後の日の2日前で、曜日が合っているか（別の計算で確かめる）
    for c in cards:
        mo, rest = c["開催日_正"].split("月")
        day = int(rest.split("日")[0])
        d = dt.date(2026, int(mo), day) if int(mo) >= 11 else dt.date(2027, int(mo), day)
        assert WD[d.weekday()] == c["開催日_正"][-2]
        e = d - dt.timedelta(days=2)
        assert c["締切_正"] == f"{e.month}月{e.day}日（{WD[e.weekday()]}）"
        assert (c["開催日_正"] != c["開催日_カード"]) or (c["時間_正"] != c["時間_カード"]) or (c["場所_正"] != c["場所_カード"])
        assert c["役に立った"] < c["去年の参加者"]
    print(f"{n}人分を作成。検算 OK")


if __name__ == "__main__":
    main()
