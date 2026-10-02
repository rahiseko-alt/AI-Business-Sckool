"""出席点（評価表①②③の共通ルール）。

「出席率100%で満点〜60%で0点、4%下がるごとに減点」。4%に満たない低下は減点しない（98%は満点）。
60%未満は0点。出席率は丸めずに分数のまま判定する。
"""

import math
from fractions import Fraction

from grading.export.provenance import format_number


def _pct(value: Fraction) -> str:
    text = format_number(value)
    return text.split("（")[1].rstrip("）") if "（" in text else text


def attendance_points(rate: Fraction, maximum: int, per_step: int) -> tuple[Fraction, str]:
    if not 0 <= rate <= 1:
        raise ValueError(f"出席率が0〜100%の範囲外: {rate}")
    percent = rate * 100
    if rate < Fraction(3, 5):
        return Fraction(0), f"出席率 {rate.numerator}/{rate.denominator}（{_pct(percent)}%）は60%未満のため0点"
    steps = math.floor((100 - percent) / 4)
    points = Fraction(maximum - per_step * steps)
    return points, (f"出席率 {rate.numerator}/{rate.denominator}（{_pct(percent)}%）→ "
                    f"4%ごとの減点{steps}回 → {maximum} − {per_step}×{steps} = {format_number(points)}")
