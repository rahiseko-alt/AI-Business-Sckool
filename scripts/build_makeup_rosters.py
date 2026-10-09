"""前期の追試の、科目ごとの出席簿（Excel）を作る。

    python3 scripts/build_makeup_rosters.py [成績表.xlsx]

入力を省くと data/input/前期成績表.xlsx（訂正入り）を、通知表と同じ計算（all_cards＋例外処置）で読む。
出力は data/output/前期追試_出席簿_2026.xlsx（個人情報のため Git には入れない）。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

from build_report_cards import all_cards  # noqa: E402
from grading.export.makeup_roster import build, targets  # noqa: E402
from grading.export.report_card_data import EXCEPTIONS_2026_FIRST  # noqa: E402
from grading.term2.first_term import apply_exceptions  # noqa: E402

INPUT = ROOT / "data" / "input" / "前期成績表.xlsx"
OUTPUT = ROOT / "data" / "output" / "前期追試_出席簿_2026.xlsx"
# 追試を受けない学生（利用者の指示、2026-10-09）: 全科目から外す
EXCLUDE = frozenset({"AIBC26008",   # BHATTARAI POOJA（プザ）
                     "AIBC26031"})  # LAMA TAMANG ROSHAN（ロサン）

if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT
    cards = apply_exceptions(all_cards(src), {(s, n): g for s, n, g, _ in EXCEPTIONS_2026_FIRST})
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    build(cards, exclude=EXCLUDE).save(OUTPUT)
    t = targets(cards, EXCLUDE)
    print(f"{len(t)}科目、のべ {sum(len(v) for v in t.values())}人 → {OUTPUT}")
