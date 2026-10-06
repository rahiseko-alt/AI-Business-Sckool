"""成果物1（タブレット貸出し）の版0〜4を作り、正解を別の計算で検算する。

使い方: python3 make_versions.py
  -> student-material-v0.md 〜 v4.md（学生に配る。v0 は練習版）
     student-log-v0.csv 〜 v4.csv（スプレッドシートにして「コピーを作成」リンクで配る）
     teacher-key.md（教員だけ）
版の配り方: 席の行と列の偶奇で 版1〜4 を決める（README）。版0 は授業の練習で使う。
"""
import csv
import datetime as dt
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# 版ごとの値: 台数N、1回の上限H（分）、誤字（正しい語 -> 誤字）
VERSIONS = {
    0: dict(N=6, H=30, typo=("図書室には", "図書質には")),
    1: dict(N=10, H=60, typo=("返す", "帰す")),
    2: dict(N=15, H=45, typo=("遅れ1回", "送れ1回")),
    3: dict(N=12, H=50, typo=("上限の時刻", "上弦の時刻")),
    4: dict(N=20, H=40, typo=("借りた時刻", "借りた自国")),
}

# 利用記録の型: (日付, 学籍番号, 借りた時刻, 上限との差（分）)。差>0 が遅れ
ROWS = [
    ("2026-10-05", "T01", "09:10", +10),
    ("2026-10-05", "T02", "10:00", -10),
    ("2026-10-06", "T03", "10:30", -5),
    ("2026-10-07", "T04", "11:00", +15),
    ("2026-10-08", "T01", "13:00", +20),
    ("2026-10-08", "T03", "13:30", -20),
    ("2026-10-09", "T02", "14:00", +5),
    ("2026-10-09", "T04", "15:00", -15),
]
IDS = ["T01", "T02", "T03", "T04"]


def add_min(hhmm, m):
    t = dt.datetime.strptime(hhmm, "%H:%M") + dt.timedelta(minutes=m)
    return t.strftime("%H:%M")


def rule(v):
    p = VERSIONS[v]
    return f"""## 材料A ルールの原文（これだけが正しい）

### つばさ国際ビジネス学院（架空） 図書室タブレット貸出し規程

**第1条（目的）** 授業の調べものに使うタブレットを、図書室で貸し出す。

**第2条（台数）** 貸し出すタブレットは{p['N']}台とする。

**第3条（貸出しの日と時間）** 平日の9時00分から17時00分まで貸し出す。土曜日・日曜日・祝日は貸し出さない。

**第4条（1回の上限）** 1回に使える時間は、借りた時刻から{p['H']}分までとする。

**第5条（遅れ）** 上限の時刻を過ぎて返した場合、遅れ1回とする。

**第6条（問い合わせ）** わからないことは、図書室のカウンターで聞く。
"""


def draft(v):
    p = VERSIONS[v]
    body = f"""## タブレットを貸し出します！

授業の調べものに、図書室のタブレットを使ってみませんか。
図書室には、タブレットが**8台**あります。

- 借りられるのは、**平日と土曜日**の 9:00〜17:00 です
- 1回に使えるのは、借りた時刻から**{p['H']}分まで**です
- 上限の時刻を過ぎて返すと、「遅れ1回」になります

わからないことは、図書室のカウンターで聞いてください。
"""
    right, wrong = p["typo"]
    assert body.count(right) >= 1, (v, right)
    body = body.replace(right, wrong, 1)
    return body


SLIDE_CARD = """## 材料D スライドの条件カード

- スライドは**ちょうど1枚**。タイトルは「タブレットの借り方」
- 必ず入れる中身: 借りられる曜日と時間／1回の上限（何分か）／上限の時刻を過ぎて返すと遅れ1回になること
- スライドの**右下**に「01」と入れる
"""

IMAGE_CARD = """## 材料E 画像の条件カード

配られた画像（ゴシック調のイラスト）を、張り紙に使うために**リアル調（写真のような見た目）**に変えてください。1枚作って提出します。
次の点は**元の画像と同じ**にしてください。

| 番号 | 条件 |
| --- | --- |
| 1 | リアル調（写真のよう）にする。とがったアーチの窓・ろうそくなど、ゴシック調の飾りを残さない |
| 2 | タブレットは**3台**のまま |
| 3 | タブレットの画面は**青**のまま |

人の顔、実在の会社・製品のロゴは入れない。
"""


def sid_of(v, sid):
    """版ごとに学籍番号を回して、隣の版と答えが同じにならないようにする。"""
    if v == 0:  # 練習版は本番の版1〜4と答えが重ならない並びにする
        return {"T01": "T01", "T02": "T03", "T03": "T02", "T04": "T04"}[sid]
    return IDS[(IDS.index(sid) + v) % len(IDS)]


def log_rows(v):
    H = VERSIONS[v]["H"]
    out = []
    for d, sid, start, diff in ROWS:
        out.append([d, sid_of(v, sid), start, add_min(start, H + diff)])
    return out


def write_all():
    keys = {}
    for v in VERSIONS:
        rows = log_rows(v)
        with open(os.path.join(OUT, f"student-log-v{v}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["日付", "学籍番号", "借りた時刻", "返した時刻"])
            w.writerows(rows)
        label = "練習版" if v == 0 else f"版{v}"
        md = f"""# 成果物1 材料（{label}）

配り方: このファイルを Google ドキュメントにして「コピーを作成」リンクで配る。材料C はスプレッドシート `student-log-v{v}.csv` を「コピーを作成」リンクで配る。
学校名・学籍番号はすべて架空。

{rule(v)}
---

## 材料B 張り紙の下書き（図書室の先輩が AI で作った。原文と照らし合わせていない）

{draft(v)}
---

## 材料C 利用記録（スプレッドシートで配る）

10月5日〜9日の貸出しの記録8行。列は 日付・学籍番号・借りた時刻・返した時刻。

---

{SLIDE_CARD}
---

{IMAGE_CARD}"""
        with open(os.path.join(OUT, f"student-material-v{v}.md"), "w", encoding="utf-8") as f:
            f.write(md)
        keys[v] = count_key(v)
    return keys


def count_key(v):
    H = VERSIONS[v]["H"]
    c = {i: 0 for i in IDS}
    for _, sid, _, diff in ROWS:
        if diff > 0:
            c[sid_of(v, sid)] += 1
    return c


def verify(keys):
    """配った CSV だけから、時刻の引き算で数え直す（count_key とは別の書き方）。"""
    for v in VERSIONS:
        H = VERSIONS[v]["H"]
        c = {i: 0 for i in IDS}
        with open(os.path.join(OUT, f"student-log-v{v}.csv"), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                a = dt.datetime.strptime(r["日付"] + " " + r["借りた時刻"], "%Y-%m-%d %H:%M")
                b = dt.datetime.strptime(r["日付"] + " " + r["返した時刻"], "%Y-%m-%d %H:%M")
                assert b.strftime("%H:%M") <= "17:00" and a.weekday() < 5
                if (b - a).total_seconds() / 60 > H:
                    c[r["学籍番号"]] += 1
        assert c == keys[v], (v, c, keys[v])
    print("verify OK: 版0〜4 の遅れの回数が一致")


def write_key(keys):
    lines = ["# 成果物1 正解表（教員だけ。学生に渡さない）", "",
             "`make_versions.py` で作り、配った CSV から別の書き方で数え直して一致を確かめた。", "",
             "## 1. 張り紙の下書きの誤り（3件。学生には数を知らせない）", "",
             "| 記号 | 下書きの文 | 正しい内容 | 原文 |", "| --- | --- | --- | --- |",
             "| E1 | タブレットが8台 | 版の台数（下の表） | 第2条 |",
             "| E2 | 平日と土曜日の 9:00〜17:00 | 平日だけ。土曜日・日曜日・祝日は借りられない | 第3条 |",
             "| T1 | 版ごとの誤字（下の表） | 正しい語 | 誤字 |", "",
             "誤りでない文（変えても✖にはしないが、原文と違う内容にしたら✖）: 1回の上限の分数（下書きは正しい）／上限を過ぎて返すと遅れ1回／カウンターで聞く。", "",
             "| 版 | 台数（E1） | 上限（分） | 誤字（T1） | 正しい語 |", "| --- | --- | --- | --- | --- |"]
    for v, p in VERSIONS.items():
        lines.append(f"| {v if v else '0（練習）'} | {p['N']}台 | {p['H']} | {p['typo'][1]} | {p['typo'][0]} |")
    lines += ["", "## 2. 集計表「結果」の正解（B2〜B5 は式であること）", "",
              "| 版 | T01 | T02 | T03 | T04 |", "| --- | --- | --- | --- | --- |"]
    for v in VERSIONS:
        lines.append(f"| {v if v else '0（練習）'} | " + " | ".join(str(keys[v][i]) for i in IDS) + " |")
    lines += ["", "版ごとに学籍番号の並びと時刻を変えてあるので、隣の版の答えを写すと合わない。"
              "教員は B2 を押して、式が出るか（数字の手打ちでないか）を見る。"
              "上限ちょうどの行は入れていない（境界は成果物2から）。", "",
              "## 3. スライド（1枚）", "",
              "| ○に必要な中身 | 1つでもあれば✖ |", "| --- | --- |",
              "| 平日の9時〜17時（土日祝は不可）／版の上限（分）／過ぎて返すと遅れ1回／右下に01 | 土曜日も借りられる、他の版の分数、2枚以上 |", "",
              "## 4. 画像", "",
              "| 条件 | 見る所 |", "| --- | --- |",
              "| 1 リアル調 | 写真のように見える。とがったアーチの窓・ろうそくが残っていない |",
              "| 2 3台 | タブレットがちょうど3台 |",
              "| 3 青 | 3台とも画面が青 |", ""]
    with open(os.path.join(OUT, "teacher-key.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    k = write_all()
    verify(k)
    write_key(k)
