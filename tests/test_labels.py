"""名前シール（A4 12面）の Excel。"""

import pytest

from grading.export.labels import LABEL_H_MM, LINE_PT, MAX_STUDENTS, build


def _students(n):
    return [("国際ビジネス科", f"AIBC26{i:03d}", f"NAME {i}") for i in range(1, n + 1)]


def test_one_label_is_42_3mm_tall():
    assert sum(LINE_PT) == pytest.approx(LABEL_H_MM / 25.4 * 72, abs=0.1)


def test_labels_read_the_roster_in_order_left_to_right():
    ws = build(_students(13))["シール"]
    assert ws["A2"].value == '=IF(名簿!$B$2="","","2026年度　"&名簿!$A$2)'
    assert ws["B3"].value == '=IF(名簿!$B$3="","",名簿!$B$3)'
    assert "名簿!$D$4" in ws["A9"].value          # 3人目は2段目の左
    assert [b.id for b in ws.row_breaks.brk] == [30]  # 13人は2枚
    assert ws.print_area == "'シール'!$A$1:$B$60"


def test_roster_has_yellow_nickname_column_and_limit():
    wb = build(_students(2))
    r = wb["名簿"]
    assert r["D1"].value.startswith("呼び名") and r["D2"].fill.fgColor.rgb == "FFFFFF00"
    with pytest.raises(ValueError):
        build(_students(MAX_STUDENTS + 1))
