"""成績表の Excel に、通知表・成績証明書のシートを式で足す（ADR 0002）。

    python3 scripts/build_report_card_excel.py [成績表.xlsx]

入力を省くと data/input/前期成績表.xlsx（AI計算版と出席簿の月別シートが入った成績表）を読む。
足すシート: 通知表データ・例外（利用者の指示による例外処置を1行書いておく）・特記事項・確認・途中の計算。
印刷用のページ（grading.export.report_card_pages.add_pages）があれば、それも足す。
出力は data/output/成績表_2026前期_通知表入り.xlsx。マクロは使わない。
式の結果は保存しない（Excel・LibreOffice で開いたときに計算される）。照合は verify_report_card_excel.py で行う。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openpyxl import load_workbook  # noqa: E402

from grading.export.report_card_data import EXCEPTIONS_2026_FIRST, add_report_card_data  # noqa: E402

INPUT = ROOT / "data" / "input" / "前期成績表.xlsx"
OUTPUT = ROOT / "data" / "output" / "成績表_2026前期_通知表入り.xlsx"


def build(source: Path = INPUT, output: Path = OUTPUT) -> Path:
    wb = load_workbook(source)
    n = add_report_card_data(wb, exceptions=EXCEPTIONS_2026_FIRST)
    try:
        from grading.export.report_card_pages import add_pages
    except ImportError:
        print("印刷用のページ（report_card_pages）がまだ無いため、データのシートだけを足す")
    else:
        add_pages(wb)
    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)
    print(f"{n}人分")
    return output


if __name__ == "__main__":
    print(build(Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT))
