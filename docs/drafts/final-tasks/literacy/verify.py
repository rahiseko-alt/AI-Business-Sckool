"""検算: 配った材料（kit と CSV）だけから正解を計算し直し、正解表 key と一致するかを確かめる。

使い方: python3 verify.py 07        （フォルダ内の kit-07.txt / responses-07.csv / key-07.md）
        python3 verify.py 01 40 DIR （DIR に作った番号版をまとめて確かめる）
make_version.py の計算は使わない（書き方を変えて、同じ答えになるかを見る）。
"""
import csv
import datetime as dt
import os
import re
import sys

WD = "月火水木金土日"


def check(no, d):
    kit = open(os.path.join(d, f"kit-{no}.txt"), encoding="utf-8").read()
    key = open(os.path.join(d, f"key-{no}.md"), encoding="utf-8").read()
    rows = list(csv.DictReader(open(os.path.join(d, f"responses-{no}.csv"), encoding="utf-8")))

    m = re.search(r"R2 定員: 第1回 (\d+)名、第2回 (\d+)名", kit)
    cap1 = int(m.group(1))
    cap2 = int(re.search(r"第2回の定員を(\d+)名に変更", kit).group(1))  # 改定後を使う
    mo, da = map(int, re.search(r"R3 申込締切: (\d+)月(\d+)日", kit).groups())
    deadline = dt.datetime(2026, mo, da, 17, 0)
    unit = int(re.search(r"R14 資料の印刷は1部(\d+)円", kit).group(1))

    def t(x):
        return dt.datetime.strptime(x["タイムスタンプ"], "%Y/%m/%d %H:%M:%S")

    def who(x):
        return x["メールアドレス"].strip().lower()

    def sess(x):
        s = x["希望回"].translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        return int(re.search(r"\d", s).group())

    b1 = sum(who(x).startswith("unei") for x in rows)
    rest = [x for x in rows if not who(x).startswith("unei")]
    b2 = sum(t(x) > deadline for x in rest)
    rest = [x for x in rest if t(x) <= deadline]
    newest = {}
    for x in rest:
        if who(x) not in newest or t(x) > t(newest[who(x)]):
            newest[who(x)] = x
    alive = sorted([x for x in newest.values() if "キャンセル" not in x["備考"]], key=t)
    q1 = [x for x in alive if sess(x) == 1]
    q2 = [x for x in alive if sess(x) == 2]
    got = {"B1": b1, "B2": b2, "B3": len(alive), "B4": min(cap1, len(q1)), "B5": min(cap2, len(q2)),
           "B6": max(0, len(q1) - cap1) + max(0, len(q2) - cap2), "B7": who(q1[cap1])}
    got["B8"] = unit * (got["B4"] + got["B5"] + 5)

    bad = []
    for k, v in got.items():
        kv = re.search(rf"\| {k} \| ([^ |]+) \|", key).group(1)
        if str(v) != kv:
            bad.append(f"{k}: 検算 {v} / 正解表 {kv}")
    # 曜日: ルール R1 は正しく、下書き 04 は第2回だけ誤り
    for (mo_, da_, w) in re.findall(r"(\d+)月(\d+)日（(.)）", kit):
        real = WD[dt.date(2026, int(mo_), int(da_)).weekday()]
        line = [ln for ln in kit.splitlines() if f"{mo_}月{da_}日（{w}）" in ln]
        in04 = any(ln.startswith("04 ") for ln in line)
        if w != real and not in04:
            bad.append(f"ルールの曜日が誤り {mo_}/{da_}")
    l04 = re.search(r"^04 .*第2回は(\d+)月(\d+)日（(.)）", kit, re.M)
    if WD[dt.date(2026, int(l04.group(1)), int(l04.group(2))).weekday()] == l04.group(3):
        bad.append("行04に曜日の誤りが入っていない")
    # 下書きの数字が正解と違う（罠が効いている）こと
    if int(re.search(r"^06 有効なお申し込みは(\d+)名", kit, re.M).group(1)) == got["B3"]:
        bad.append("行06が正解と同じ")
    if int(re.search(r"^13 .*＝(\d+)円", kit, re.M).group(1)) == got["B8"]:
        bad.append("行13が正解と同じ")
    # 罠が効いていること: 雑なやり方だと答えが変わる
    dateonly = sum(t(x).date() > deadline.date() for x in rows if not who(x).startswith("unei"))
    exact = {x["メールアドレス"]: x for x in sorted(rest, key=t)}
    casesens = sum("キャンセル" not in x["備考"] for x in exact.values())
    q2old = min(int(m.group(2)), len(q2))
    if dateonly == b2 or casesens == got["B3"] or q2old == got["B5"]:
        bad.append("罠が効いていない")
    return got, bad


if __name__ == "__main__":
    lo = int(sys.argv[1])
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else lo
    d = sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(os.path.abspath(__file__))
    ng = 0
    for i in range(lo, hi + 1):
        got, bad = check(f"{i:02d}", d)
        ng += bool(bad)
        print(f"{i:02d}", "OK" if not bad else "NG " + "; ".join(bad), got)
    print(f"{hi - lo + 1}版中 NG {ng}")
