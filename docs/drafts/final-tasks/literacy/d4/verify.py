"""成果物4の検算: kit のルールと CSV だけから B1〜B6 と曜日を別の書き方で計算し直し、key と照合する。
使い方: python3 verify.py 1 40"""
import calendar, csv, os, re, sys
from datetime import datetime
OUT = os.environ.get("LIT_OUT", os.path.dirname(os.path.abspath(__file__)))
WD = "月火水木金土日"
ng = 0
for i in range(int(sys.argv[1]), int(sys.argv[-1]) + 1):
    no = f"{i:02d}"
    kit = open(os.path.join(OUT, f"kit-{no}.txt"), encoding="utf-8").read()
    key = open(os.path.join(OUT, f"key-{no}.md"), encoding="utf-8").read()
    c1, c2 = map(int, re.search(r"R2 定員: 第1回 (\d+)名、第2回 (\d+)名", kit).groups())
    mo, d = map(int, re.search(r"R3 申込締切: (\d+)月(\d+)日", kit).groups())
    dl = datetime(2026, mo, d, 17, 0)
    m1, d1 = map(int, re.search(r"R1 講座: 第1回 (\d+)月(\d+)日", kit).groups())
    rows = list(csv.reader(open(os.path.join(OUT, f"responses-{no}.csv"), encoding="utf-8")))[1:]
    best = {}
    for r in rows:
        t = datetime.strptime(r[0], "%Y/%m/%d %H:%M:%S")
        m = r[1].strip().lower()
        if m.startswith("unei") or t > dl:
            continue
        if m not in best or t > best[m][0]:
            best[m] = (t, r[3], r[4])
    live = sorted(((t, m, s) for m, (t, s, note) in best.items() if "キャンセル" not in note))
    q1 = [m for t, m, s in live if s == "第1回"]
    q2 = [m for t, m, s in live if s == "第2回"]
    want = [f"| B1 | {len(live)} |", f"| B2 | {min(c1, len(q1))} |", f"| B3 | {min(c2, len(q2))} |",
            f"| B4 | {max(0, len(q1) - c1)} |", f"| B5 | {q1[c1]} |", f"| B6 | {q1[c1 - 1]} |",
            f"| 04 | 曜日 | {m1}月{d1}日（{WD[calendar.weekday(2026, m1, d1)]}） |", f"有効なお申し込みは{len(q1)}名"]
    ok = all(x in key for x in want)
    ng += not ok
    print(no, "OK" if ok else "NG", len(live), len(q1), q1[c1])
print("NG", ng)
