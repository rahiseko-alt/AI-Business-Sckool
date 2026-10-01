from decimal import Decimal

import pytest

from grading.domain.enums import ValueKind
from grading.normalization import NameDiff, compare_names, normalize_name, parse_value


@pytest.mark.parametrize("original", ["田中太郎", "田中 太郎", "田中　太郎", " 田中 太郎 "])
def test_spacing_and_width_variants_normalize_to_the_same_name(original):
    assert normalize_name(original) == "田中太郎"


def test_romaji_is_normalized_case_and_space_insensitively():
    assert normalize_name("Tanaka  Taro") == normalize_name("ＴＡＮＡＫＡ　ＴＡＲＯ") == "TANAKATARO"


def test_different_characters_are_never_treated_as_the_same_name():
    assert compare_names("田中 太郎", "田中 太朗") == NameDiff.DIFFERENT


def test_identical_and_format_only_differences_are_distinguished():
    assert compare_names("田中 太郎", "田中 太郎") == NameDiff.IDENTICAL
    assert compare_names("田中 太郎", "田中　太郎") == NameDiff.FORMAT_ONLY


@pytest.mark.parametrize("original", [None, "", "   "])
def test_blank_is_blank_not_zero(original):
    v = parse_value(original, markers={})
    assert v.kind == ValueKind.BLANK and v.number is None


@pytest.mark.parametrize("original", [0, "0", "０", "0.0"])
def test_zero_is_a_recorded_zero_not_blank_or_absent(original):
    v = parse_value(original, markers={})
    assert v.kind == ValueKind.ZERO and v.number == Decimal("0")


@pytest.mark.parametrize("original, expected", [(85, "85"), ("85", "85"), ("８５", "85"), (87.5, "87.5")])
def test_numbers_are_parsed_exactly(original, expected):
    v = parse_value(original, markers={})
    assert v.kind == ValueKind.NUMBER and v.number == Decimal(expected)


def test_text_marks_are_unknown_unless_a_rule_defines_them():
    assert parse_value("未提出", markers={}).kind == ValueKind.UNKNOWN
    assert parse_value("欠", markers={}).kind == ValueKind.UNKNOWN
    markers = {"未提出": ValueKind.NOT_SUBMITTED, "欠": ValueKind.ABSENT}
    assert parse_value("未提出", markers=markers).kind == ValueKind.NOT_SUBMITTED
    assert parse_value(" 欠 ", markers=markers).kind == ValueKind.ABSENT


def test_original_value_is_kept_verbatim():
    assert parse_value("８５", markers={}).original == "８５"


def test_booleans_are_not_numbers():
    assert parse_value(True, markers={}).kind == ValueKind.UNKNOWN


@pytest.mark.parametrize("original", ["٨٥", "𝟗𝟎"])
def test_non_ascii_digits_are_not_numbers(original):
    assert parse_value(original, markers={}).kind == ValueKind.UNKNOWN
