"""通知表入りの成績表を LibreOffice で再計算し、「通知表データ」を report_card.py の計算と全員分照合する（ADR 0002）。

    python3 scripts/verify_report_card_excel.py [通知表入りの成績表.xlsx] [元の成績表.xlsx]

既定は data/output/成績表_2026前期_通知表入り.xlsx と data/input/前期成績表.xlsx。
食い違いは学籍番号・科目・項目だけを出す（点数や氏名は出さない）。食い違いがあれば終了コード1。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from build_ai_version import recalculated  # noqa: E402
from build_report_card_excel import INPUT, OUTPUT  # noqa: E402
from build_report_cards import all_cards  # noqa: E402

from grading.export.report_card_data import CHECK, DATA, EXCEPTIONS_2026_FIRST, compare, expected_cards  # noqa: E402


def verify(built: Path = OUTPUT, source: Path = INPUT) -> list:
    values = recalculated(built)
    cards = expected_cards(all_cards(source), EXCEPTIONS_2026_FIRST)
    problems = compare(values[DATA], cards)
    print(f"{len(cards)}人を照合: 食い違い {len(problems)}件、確認シートの要確認 {values[CHECK]['B2'].value}件")
    for p in problems:
        print(*p)
    return problems


if __name__ == "__main__":
    args = [Path(a) for a in sys.argv[1:]]
    sys.exit(1 if verify(*args) else 0)
