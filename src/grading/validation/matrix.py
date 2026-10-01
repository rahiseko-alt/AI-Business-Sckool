"""学生×科目の完全性マトリクス。履修の組み合わせは推測せず、expected として明示的に受け取る。"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum

from grading.domain.enums import DataStatus


_PRESENT = (DataStatus.CONFIRMED, DataStatus.WARNING)


class Cell(StrEnum):
    OK = "OK"
    OK_WARNING = "OK(要確認)"
    UNRESOLVED = "??"
    MISSING = "NG"
    NOT_ENROLLED = "—"


@dataclass(frozen=True)
class Matrix:
    students: tuple[str, ...]
    subjects: tuple[str, ...]
    cells: Mapping[str, Mapping[str, Cell]]
    expected: frozenset[tuple[str, str]]
    results: Mapping[tuple[str, str], DataStatus]
    unexpected: tuple[tuple[str, str], ...]   # 履修していない・存在しない組み合わせの結果
    off_axis: tuple[tuple[str, str], ...]     # 学生一覧・科目一覧に無い履修

    def gaps(self) -> list[tuple[str, str]]:
        """欠損・未確定の組み合わせ。表の軸ではなく、履修の組み合わせそのものから数える。"""
        return sorted(p for p in self.expected if self.results.get(p) not in _PRESENT)

    @property
    def complete(self) -> bool:
        return bool(self.expected) and not self.gaps() and not self.unexpected and not self.off_axis


def completeness_matrix(
    students: Iterable[str],
    subjects: Iterable[str],
    expected: set[tuple[str, str]],
    results: Mapping[tuple[str, str], DataStatus],
) -> Matrix:
    students, subjects = tuple(students), tuple(subjects)
    cells: dict[str, dict[str, Cell]] = {}
    for s in students:
        cells[s] = {}
        for sub in subjects:
            status = results.get((s, sub))
            if (s, sub) not in expected:
                cells[s][sub] = Cell.NOT_ENROLLED
            elif status is None:
                cells[s][sub] = Cell.MISSING
            elif status == DataStatus.CONFIRMED:
                cells[s][sub] = Cell.OK
            elif status == DataStatus.WARNING:
                cells[s][sub] = Cell.OK_WARNING
            else:
                cells[s][sub] = Cell.UNRESOLVED
    unexpected = tuple(sorted(k for k in results if k not in expected))
    off_axis = tuple(sorted(p for p in expected if p[0] not in students or p[1] not in subjects))
    return Matrix(students, subjects, cells, frozenset(expected), dict(results), unexpected, off_axis)
