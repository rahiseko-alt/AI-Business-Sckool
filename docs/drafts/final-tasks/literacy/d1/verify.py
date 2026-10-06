"""成果物1の検算: kit だけから正解を計算し直し、key と照合する。
使い方: python3 verify.py 1 40   （make.py と同じ LIT_SALT・LIT_OUT で先に作っておく）"""
import calendar, os, re, sys
OUT = os.environ.get("LIT_OUT", os.path.dirname(os.path.abspath(__file__)))
WD = "月火水木金土日"
ng = 0
for i in range(int(sys.argv[1]), int(sys.argv[-1]) + 1):
    no = f"{i:02d}"
    kit = open(os.path.join(OUT, f"kit-{no}.txt"), encoding="utf-8").read()
    key = open(os.path.join(OUT, f"key-{no}.md"), encoding="utf-8").read()
    m2 = kit.split("--- メール2 ---")[1].split("--- メール3 ---")[0]
    m3 = kit.split("--- メール3 ---")[1].split("--- メール4 ---")[0]
    m4 = kit.split("--- メール4 ---")[1]
    mo, d = map(int, re.search(r"翌週の(\d+)月(\d+)日", m2).groups())
    h, mi = map(int, re.search(r"(\d+):(\d+)〜", kit.split("--- メール1 ---")[1]).groups())
    eh, emi = map(int, re.search(r"〜(\d+):(\d+)", kit.split("--- メール1 ---")[1]).groups())
    delta = int(re.search(r"それぞれ(\d+)分", m4).group(1))
    room = re.search(r"同じ時間なら(.+?)をお取り", m3).group(1)
    w = WD[calendar.weekday(2026, mo, d)]
    s = h * 60 + mi + delta
    e = eh * 60 + emi + delta
    want = [f"日にち：{mo}月{d}日（{w}）", f"時間：{s // 60}:{s % 60:02d}〜{e // 60}:{e % 60:02d}", f"会場：{room}"]
    ok = all(x in key for x in want)
    ng += not ok
    print(no, "OK" if ok else "NG", want)
print("NG", ng)
