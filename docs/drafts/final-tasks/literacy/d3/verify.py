"""成果物3の検算: 最新の申込CSVだけから B1〜B3 を別の書き方で数え直し、key と照合する。
使い方: python3 verify.py 1 40"""
import csv, os, sys
from datetime import datetime
OUT = os.environ.get("LIT_OUT", os.path.dirname(os.path.abspath(__file__)))
DL = datetime(2026, 11, 16, 17, 0)
ng = 0
for i in range(int(sys.argv[1]), int(sys.argv[-1]) + 1):
    no = f"{i:02d}"
    rows = list(csv.reader(open(os.path.join(OUT, "data", f"申込-{no}-1116.csv"), encoding="utf-8")))[2:]
    rows = [(datetime.strptime(r[0], "%Y/%m/%d %H:%M:%S"), r[1].strip().lower(), r[4]) for r in rows]
    b1 = sum(1 for r in rows if r[1].startswith("unei"))
    b2 = sum(1 for r in rows if not r[1].startswith("unei") and r[0] > DL)
    last = {}
    for t, m, note in rows:
        if m.startswith("unei") or t > DL:
            continue
        if m not in last or t > last[m][0]:
            last[m] = (t, note)
    b3 = sum(1 for t, note in last.values() if "キャンセル" not in note)
    key = open(os.path.join(OUT, f"key-{no}.md"), encoding="utf-8").read()
    want = [f"| B1 テスト送信の行数 | {b1} |", f"| B2 締切後に届いた行数 | {b2} |", f"| B3 有効な申込の人数 | {b3} |", f"人数 **{b3}名**"]
    ok = all(x in key for x in want)
    ng += not ok
    print(no, "OK" if ok else "NG", b1, b2, b3)
print("NG", ng)
