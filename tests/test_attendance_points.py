from fractions import Fraction

import pytest

from grading.rules.attendance_points import attendance_points


@pytest.mark.parametrize("rate, expected", [
    (Fraction(1), 10), (Fraction(98, 100), 10), (Fraction(96, 100), 9), (Fraction(9601, 10000), 10),
    (Fraction(95, 100), 9), (Fraction(92, 100), 8), (Fraction(64, 100), 1), (Fraction(60, 100), 0),
    (Fraction(599, 1000), 0), (Fraction(0), 0),
])
def test_ten_point_scale_drops_one_point_per_full_four_percent(rate, expected):
    assert attendance_points(rate, maximum=10, per_step=1)[0] == expected


@pytest.mark.parametrize("rate, expected", [(Fraction(1), 20), (Fraction(97, 100), 20), (Fraction(96, 100), 18),
                                            (Fraction(61, 100), 2), (Fraction(60, 100), 0)])
def test_twenty_point_scale_drops_two_points_per_full_four_percent(rate, expected):
    assert attendance_points(rate, maximum=20, per_step=2)[0] == expected


def test_explanation_shows_the_rate_exactly_and_the_steps():
    points, text = attendance_points(Fraction(29, 30), maximum=10, per_step=1)
    assert points == 10
    assert "29/30" in text and "減点0回" in text


def test_rate_outside_zero_to_one_is_refused():
    with pytest.raises(ValueError):
        attendance_points(Fraction(11, 10), maximum=10, per_step=1)
