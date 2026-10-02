"""ほかのAI（ChatGPT・Gemini など）にレビューさせるための資料一式を作る。

    python3 scripts/make_review_packet.py

data/output/レビュー依頼.zip ができる。中身:
  依頼文.md      … そのままAIに貼り付ける指示文
  決まり.md      … 守るべき原則・利用者が確定した決まり・採点の決まり
  検算結果.txt   … こちらの検算の結果（AIにはこれを信用せず数え直すよう指示している）
  資料/          … 出席簿・元の成績表・出来上がった成績ファイル
学生の個人情報が入るので、渡す先は利用者が判断する。
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_ai_version import CHECK_REPORT, DATA, DEPTS, OUTPUT  # noqa: E402
import build_ai_version  # noqa: E402

PACKET = DATA / "output" / "レビュー依頼.zip"

REQUEST = """# 成績ファイルの検算レビューのお願い

あなたは独立したレビュー担当です。添付の「決まり.md」だけを根拠に、「資料/」の元資料から自分で数え直し、
出来上がった成績ファイル（{output}）が正しいか確かめてください。「検算結果.txt」は作った側の自己申告なので、信用せず照合に使わないでください。

## 資料
{files}

## 確かめること
1. 出席簿の月別シート（「4月」〜「9月」）から、学生ごと・科目ごとに授業数（×を除く）・欠・遅を数える。
   日本語運用力強化演習は1週＝1回（その週に1回でも出席なら出席、出席が無く遅があれば遅刻、ほかは欠席）。
2. 決まり.md の式で出席点・出席率・態度点を計算し、成績ファイルの「AI計算版_国際」「AI計算版_総合」の色付きセルと全件照合する。
3. 色の付いていないセルが、元の成績表（file3_ai.xlsx＝国際、file4.xlsx＝総合）と同じか確かめる。
4. 「個人別評定」「E一覧」「テスト分析」「偏差値」「度数分布」を抜き取りで手計算し、合っているか確かめる。
5. 推測で埋めた値・空欄を0とした扱い・別科目の決まりの流用・丸め・根拠の無い数字が無いか探す。

## 返事の形（この形だけで）
- 判定: 合格／不合格／判断できない
- 照合した件数: 項目ごとに「何件照合し、何件食い違ったか」
- 食い違い: 1件ずつ「シート・学籍番号・科目・項目・表の値・あなたの計算値・根拠のセル」
- 疑問: 決まりが無い、資料が矛盾しているなど、人に確認すべき点
- 確認できなかったこと: 読めなかった資料や照合しなかった範囲

わからないことは推測せず「わからない」と書いてください。学生の氏名は返事に書かず、学籍番号だけを書いてください。
"""


def rules_text() -> str:
    adr = (ROOT / "docs" / "adr" / "0001-no-inference-halt-and-trace.md").read_text(encoding="utf-8")
    decisions = json.loads((DATA / "input" / "decisions.json").read_text(encoding="utf-8"))["decisions"]
    lines = ["# 決まり", "", "## 採点の決まり（生成スクリプトの説明）", "", "```", build_ai_version.__doc__.strip(), "```", "",
             "## 利用者が確定した決まり（Decision Log）", ""]
    lines += [f"- {d['id']}: {d.get('resolved') or d.get('answer')}" for d in decisions]
    lines += ["", "## 守るべき原則", "", adr]
    return "\n".join(lines) + "\n"


def make_packet() -> Path:
    if not OUTPUT.exists():
        raise SystemExit(f"{OUTPUT.name} が無い。先に scripts/build_ai_version.py を実行して検算に合格させること")
    work = Path(tempfile.mkdtemp()) / "レビュー依頼"
    (work / "資料").mkdir(parents=True)
    sources = [DATA / "input" / name for reg, orig, _ in DEPTS for name in (reg, orig)] + [OUTPUT]
    for src in sources:
        shutil.copy(src, work / "資料" / src.name)
    files = "\n".join(f"- 資料/{s.name}" for s in sources)
    (work / "依頼文.md").write_text(REQUEST.format(output=f"資料/{OUTPUT.name}", files=files), encoding="utf-8")
    (work / "決まり.md").write_text(rules_text(), encoding="utf-8")
    if CHECK_REPORT.exists():
        shutil.copy(CHECK_REPORT, work / CHECK_REPORT.name)
    PACKET.unlink(missing_ok=True)
    return Path(shutil.make_archive(str(PACKET.with_suffix("")), "zip", work.parent, work.name))


if __name__ == "__main__":
    print(make_packet())
