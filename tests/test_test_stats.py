import math

import pytest

from grading.analysis.test_stats import deviation_scores, judge, summarize


def test_summary_of_a_balanced_test():
    s = summarize([40, 50, 60, 70, 80], maximum=100)
    assert (s.n, s.mean, s.rate, s.minimum, s.maximum_score, s.median) == (5, 60, 0.6, 40, 80, 60)
    assert s.sd == pytest.approx(math.sqrt(200))           # 母標準偏差
    assert s.full_marks == 0 and s.zeros == 0
    assert s.bins == (0, 0, 0, 0, 1, 1, 1, 1, 1, 0)        # 0-10%,…,90-100%
    assert judge(s) == ("適正", [])


def test_easy_test_is_flagged_by_ceiling_effect():
    s = summarize([90, 100, 100, 100, 80], maximum=100)
    verdict, reasons = judge(s)
    assert verdict == "易しすぎ" and any("天井" in r for r in reasons)


def test_hard_test_is_flagged_by_floor_effect():
    verdict, reasons = judge(summarize([0, 5, 10, 30, 2], maximum=100))
    assert verdict == "難しすぎ" and any("床" in r for r in reasons)


def test_test_that_does_not_separate_students():
    verdict, reasons = judge(summarize([60, 62, 61, 63, 60], maximum=100))
    assert verdict == "差がつかない" and any("ばらつき" in r for r in reasons)


def test_deviation_scores_use_mean_50_and_sd_10():
    d = deviation_scores({"a": 40, "b": 60, "c": 80})
    assert d["b"] == pytest.approx(50) and d["c"] == pytest.approx(50 + 10 * 20 / math.sqrt(800 / 3))


def test_no_spread_gives_no_deviation_score():
    assert deviation_scores({"a": 5, "b": 5}) == {"a": None, "b": None}


def test_empty_input_is_refused():
    with pytest.raises(ValueError):
        summarize([], maximum=10)
