"""成果物2の検算: card と CSV だけから人数と期限を計算し直し、key と照合する。
使い方: python3 verify.py 1 15"""
import csv, datetime as dt, os, re, sys
OUT = os.environ.get("LIT_OUT", os.path.dirname(os.path.abspath(__file__)))
WD = "月火水木金土日"
ng = 0
for i in range(int(sys.argv[1]), int(sys.argv[-1]) + 1):
    no = f"{i:02d}"
    card = open(os.path.join(OUT, f"card-{no}.txt"), encoding="utf-8").read()
    key = open(os.path.join(OUT, f"key-{no}.md"), encoding="utf-8").read()
    for n, tag in ((1, "A"), (2, "B")):
        blk = card.split(f"■ 会議{n}（")[1].split("■ ")[0]
        mo, md = map(int, re.search(r"時刻: (\d+)月(\d+)日", blk).groups())
        meet = dt.date(2026, mo, md)
        co, cd = map(int, re.search(r"第\d回　(\d+)月(\d+)日", blk).groups())
        course = dt.date(2026, co, cd)
        dm, dd, dh = map(int, re.search(r"締切は (\d+)月(\d+)日 (\d+):00", blk).groups())
        deadline = dt.datetime(2026, dm, dd, dh)
        people = set()
        with open(os.path.join(OUT, f"responses-{no}-{tag}.csv"), encoding="utf-8") as f:
            for row in list(csv.reader(f))[1:]:
                t = dt.datetime.strptime(row[0], "%Y/%m/%d %H:%M:%S")
                if row[1].lower().startswith("unei") or t > deadline:
                    continue
                people.add(row[1].strip().lower())
        want = [f"報告の人数: **{len(people)}名**"]
        sec = key.split(f"## 会議{n}")[1]
        for k, m in enumerate(re.finditer(r"(講座の日の|会議の日から)(\d+)日(前|後)の(\d+):(\d+)", blk), 1):
            base = course if m.group(1) == "講座の日の" else meet
            days = int(m.group(2)) * (-1 if m.group(3) == "前" else 1)
            t = dt.datetime.combine(base + dt.timedelta(days=days), dt.time(int(m.group(4)), int(m.group(5))))
            while t.weekday() >= 5:
                t -= dt.timedelta(days=1)
            want.append(f"| ToDo{k} | {t.month}月{t.day}日（{WD[t.weekday()]}）{t.hour}:{t.minute:02d} |")
        ok = all(x in (key if x.startswith("報告") and False else sec) for x in want)
        ng += not ok
        print(no, n, "OK" if ok else "NG", want)
print("NG", ng)
