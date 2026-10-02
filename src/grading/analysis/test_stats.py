"""テスト1つ分の統計と適正度の判定、偏差値。

設問ごとの得点が無いので、テスト全体の得点だけで判定する。判定の目安（一般的なもの。学校で調整できる）:
- 易しすぎ: 平均得点率85%以上、または天井効果（平均＋標準偏差が満点を超える）
- 難しすぎ: 平均得点率40%未満、または床効果（平均−標準偏差が0を下回る）
- 差がつかない: 標準偏差が満点の10%未満
標準偏差は母標準偏差（偏差値の計算と同じ）。
"""


import statistics
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

EASY_RATE, HARD_RATE, MIN_SPREAD = 0.85, 0.40, 0.10


@dataclass(frozen=True)
class TestSummary:
    n: int
    maximum: float
    mean: float
    rate: float
    sd: float
    minimum: float
    maximum_score: float
    median: float
    full_marks: int
    zeros: int
    bins: tuple[int, ...]       # 得点率 0-10%, 10-20%, …, 90-100%（100%は最後に入れる）


def summarize(scores: Sequence[float], maximum: float) -> TestSummary:
    if not scores:
        raise ValueError("得点が1つも無い")
    mean = statistics.fmean(scores)
    bins = [0] * 10
    for s in scores:
        bins[min(int(s / maximum * 10), 9)] += 1
    return TestSummary(len(scores), maximum, mean, mean / maximum, statistics.pstdev(scores), min(scores),
                       max(scores), statistics.median(scores), sum(1 for s in scores if s >= maximum),
                       sum(1 for s in scores if s == 0), tuple(bins))


def judge(s: TestSummary) -> tuple[str, list[str]]:
    easy, hard, flat = [], [], []
    if s.rate >= EASY_RATE:
        easy.append(f"平均得点率{s.rate:.0%}が{EASY_RATE:.0%}以上")
    if s.mean + s.sd > s.maximum:
        easy.append("天井効果（平均＋標準偏差が満点を超える）")
    if s.rate < HARD_RATE:
        hard.append(f"平均得点率{s.rate:.0%}が{HARD_RATE:.0%}未満")
    if s.mean - s.sd < 0:
        hard.append("床効果（平均−標準偏差が0を下回る）")
    if s.sd < MIN_SPREAD * s.maximum:
        flat.append(f"ばらつきが小さい（標準偏差が満点の{MIN_SPREAD:.0%}未満）")
    if easy:
        return "易しすぎ", easy + flat
    if hard:
        return "難しすぎ", hard + flat
    if flat:
        return "差がつかない", flat
    return "適正", []


def deviation_scores(scores: Mapping[str, float]) -> dict[str, float | None]:
    """偏差値＝50＋10×（得点−平均）÷標準偏差。全員同点なら計算できないので None。"""
    values = list(scores.values())
    mean, sd = statistics.fmean(values), statistics.pstdev(values)
    return {k: (50 + 10 * (v - mean) / sd if sd else None) for k, v in scores.items()}


def correlation(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    if len(xs) < 3 or statistics.pstdev(xs) == 0 or statistics.pstdev(ys) == 0:
        return None
    return statistics.correlation(xs, ys)



