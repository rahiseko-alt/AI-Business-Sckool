from collections.abc import Sequence
from dataclasses import dataclass

from grading.domain.enums import DataStatus, MatchStatus
from grading.normalization import NameDiff, compare_names, fold_width, normalize_token


@dataclass(frozen=True)
class Student:
    student_key: str
    student_number: str | None
    name: str
    class_: str | None = None
    seat_number: int | None = None
    email: str | None = None
    school_id: str | None = None
    name_roman: str | None = None


@dataclass(frozen=True)
class IdentityClaim:
    """資料の1行が名乗っている学生。分かる項目だけ埋める。"""

    student_number: str | None = None
    name: str | None = None
    class_: str | None = None
    seat_number: int | None = None
    email: str | None = None
    school_id: str | None = None


@dataclass(frozen=True)
class Match:
    status: MatchStatus
    student_key: str | None          # CONFIRMED のときだけ入る
    candidates: tuple[str, ...]
    data_status: DataStatus
    reasons: tuple[str, ...] = ()


_STRONG = ("student_number", "email", "school_id")


def _token(value: object) -> str | None:
    return None if value is None or str(value).strip() == "" else normalize_token(str(value))


def _id(field: str, value: object) -> str | None:
    """強いIDの比較用。学籍番号・学校IDは大文字小文字を区別し、メールだけ区別しない。"""
    if value is None or str(value).strip() == "":
        return None
    text = fold_width(str(value)).strip()
    return text.casefold() if field == "email" else text


def _check_unique(master: Sequence[Student]) -> None:
    for field in _STRONG:
        seen: dict[str, str] = {}
        for s in master:
            key = _id(field, getattr(s, field))
            if key is None:
                continue
            if key in seen:
                raise ValueError(f"duplicate {field} in student master: {seen[key]} / {s.student_key}")
            seen[key] = s.student_key


def _name_diff(claim_name: str, s: Student) -> NameDiff:
    diffs = [compare_names(claim_name, s.name)]
    if s.name_roman:
        roman = compare_names(claim_name, s.name_roman)
        diffs.append(NameDiff.FORMAT_ONLY if roman == NameDiff.IDENTICAL else roman)
    for d in (NameDiff.IDENTICAL, NameDiff.FORMAT_ONLY):
        if d in diffs:
            return d
    return NameDiff.DIFFERENT


def _matches_weak(claim: IdentityClaim, s: Student) -> bool:
    if claim.name is not None and _name_diff(claim.name, s) == NameDiff.DIFFERENT:
        return False
    if claim.class_ is not None and _token(claim.class_) != _token(s.class_):
        return False
    if claim.seat_number is not None and claim.seat_number != s.seat_number:
        return False
    return True


def _blocked(status: MatchStatus, candidates: list[Student], reason: str) -> Match:
    keys = tuple(dict.fromkeys(s.student_key for s in candidates))
    return Match(status, None, keys, DataStatus.BLOCKED, (reason,))


def resolve(claim: IdentityClaim, master: Sequence[Student]) -> Match:
    _check_unique(master)

    strong_given = [f for f in _STRONG if _id(f, getattr(claim, f)) is not None]
    if strong_given:
        hits: dict[str, Student] = {}
        for field in strong_given:
            found = [s for s in master if _id(field, getattr(s, field)) == _id(field, getattr(claim, field))]
            if not found:
                return _blocked(MatchStatus.UNMATCHED, [], f"{field} が学生マスターに存在しない")
            hits[found[0].student_key] = found[0]
        if len(hits) > 1:
            return _blocked(MatchStatus.AMBIGUOUS, list(hits.values()), "ID同士が別の学生を指している")
        student = next(iter(hits.values()))
        if not _matches_weak(claim, student):
            others = [s for s in master if s is not student and _matches_weak(claim, s)]
            return _blocked(MatchStatus.AMBIGUOUS, [student, *others], "IDと氏名・クラス・出席番号が食い違う")
        warnings = []
        if claim.name is not None and _name_diff(claim.name, student) == NameDiff.FORMAT_ONLY:
            warnings.append("氏名の表記（空白・全角半角・ローマ字）のみ異なる")
        if claim.class_ is not None and claim.class_ != student.class_:
            warnings.append("クラスの表記（全角半角）のみ異なる")
        status = DataStatus.WARNING if warnings else DataStatus.CONFIRMED
        return Match(MatchStatus.CONFIRMED, student.student_key, (student.student_key,), status, tuple(warnings))

    if claim.name is None and claim.class_ is None and claim.seat_number is None:
        return _blocked(MatchStatus.UNMATCHED, [], "学生を特定する手がかりが無い")
    found = [s for s in master if _matches_weak(claim, s)]
    if not found:
        return _blocked(MatchStatus.UNMATCHED, [], "該当する学生がいない")
    if len(found) == 1:
        return _blocked(MatchStatus.LIKELY, found, "ID無しの一致は確定に使わない")
    return _blocked(MatchStatus.AMBIGUOUS, found, "同じ手がかりの学生が複数いる")
