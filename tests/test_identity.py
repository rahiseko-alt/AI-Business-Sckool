import pytest

from grading.domain.enums import DataStatus, MatchStatus
from grading.identity import IdentityClaim, Student, resolve

TANAKA_1A = Student("S00123", "20260031", "田中 太郎", "1A", 14, "t31@example.jp", name_roman="TANAKA TARO")
TANAKA_1B = Student("S00456", "20260082", "田中 太郎", "1B", 8, "t82@example.jp")
SATO = Student("S00789", "20260050", "佐藤 花子", "1A", 20)
MASTER = [TANAKA_1A, TANAKA_1B, SATO]


def test_student_number_and_name_match_is_confirmed():
    m = resolve(IdentityClaim(student_number="20260031", name="田中 太郎", class_="1A"), MASTER)
    assert (m.status, m.student_key, m.data_status) == (MatchStatus.CONFIRMED, "S00123", DataStatus.CONFIRMED)


def test_format_only_name_difference_is_confirmed_with_warning():
    m = resolve(IdentityClaim(student_number="20260031", name="田中　太郎", class_="１Ａ"), MASTER)
    assert (m.status, m.student_key, m.data_status) == (MatchStatus.CONFIRMED, "S00123", DataStatus.WARNING)
    assert m.reasons


def test_romaji_name_with_student_number_is_confirmed_with_warning():
    m = resolve(IdentityClaim(student_number="20260031", name="TANAKA TARO"), MASTER)
    assert (m.status, m.data_status) == (MatchStatus.CONFIRMED, DataStatus.WARNING)


def test_name_only_with_homonyms_is_ambiguous_and_blocked():
    m = resolve(IdentityClaim(name="田中 太郎"), MASTER)
    assert m.status == MatchStatus.AMBIGUOUS and m.data_status == DataStatus.BLOCKED
    assert m.student_key is None
    assert set(m.candidates) == {"S00123", "S00456"}


def test_unique_name_without_strong_id_is_only_likely_and_blocked():
    m = resolve(IdentityClaim(name="佐藤 花子", class_="1A"), MASTER)
    assert m.status == MatchStatus.LIKELY and m.data_status == DataStatus.BLOCKED
    assert m.student_key is None and m.candidates == ("S00789",)


def test_class_narrows_homonyms_but_still_needs_confirmation():
    m = resolve(IdentityClaim(name="田中 太郎", class_="1B"), MASTER)
    assert m.status == MatchStatus.LIKELY and m.candidates == ("S00456",)


def test_one_character_difference_is_not_matched_to_the_number_owner():
    m = resolve(IdentityClaim(student_number="20260031", name="田中 太朗"), MASTER)
    assert m.status == MatchStatus.AMBIGUOUS and m.data_status == DataStatus.BLOCKED


def test_class_contradicting_the_student_number_is_blocked():
    m = resolve(IdentityClaim(student_number="20260031", name="田中 太郎", class_="1B"), MASTER)
    assert m.status == MatchStatus.AMBIGUOUS and m.data_status == DataStatus.BLOCKED
    assert set(m.candidates) == {"S00123", "S00456"}


def test_nonexistent_student_number_is_unmatched():
    m = resolve(IdentityClaim(student_number="99999999", name="田中 太郎"), MASTER)
    assert m.status == MatchStatus.UNMATCHED and m.data_status == DataStatus.BLOCKED


def test_strong_ids_pointing_to_different_students_are_blocked():
    m = resolve(IdentityClaim(student_number="20260031", email="t82@example.jp"), MASTER)
    assert m.status == MatchStatus.AMBIGUOUS and set(m.candidates) == {"S00123", "S00456"}


def test_email_alone_with_matching_name_is_confirmed():
    m = resolve(IdentityClaim(email="T82@Example.jp", name="田中 太郎"), MASTER)
    assert (m.status, m.student_key) == (MatchStatus.CONFIRMED, "S00456")


def test_unknown_name_without_ids_is_unmatched():
    assert resolve(IdentityClaim(name="山田 一郎"), MASTER).status == MatchStatus.UNMATCHED


def test_claim_without_any_identifier_is_unmatched():
    assert resolve(IdentityClaim(), MASTER).status == MatchStatus.UNMATCHED


def test_duplicate_student_number_in_master_is_rejected():
    dup = Student("S00999", "20260031", "別人", "1C", 1)
    with pytest.raises(ValueError, match="duplicate"):
        resolve(IdentityClaim(student_number="20260031"), [*MASTER, dup])
