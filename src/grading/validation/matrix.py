"""学生×科目の完全性マトリクス。履修の組み合わせは推測せず、expected として明示的に受け取る。"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum

from grading.domain.enums import DataStatus


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
    unexpected: tuple[tuple[str, str], ...]   # 履修していない・存在しない組み合わせの結果

    def gaps(self) -> list[tuple[str, str]]:
        return [(s, sub) for s in self.students for sub in self.subjects
                if self.cells[s][sub] in (Cell.UNRESOLVED, Cell.MISSING)]

    @property
    def complete(self) -> bool:
        return not self.gaps() and not self.unexpected


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
            elif status == DataStatus.BLOCKED:
                cells[s][sub] = Cell.UNRESOLVED
            else:
                cells[s][sub] = Cell.OK if status == DataStatus.CONFIRMED else Cell.OK_WARNING
    unexpected = tuple(sorted(k for k in results if k not in expected))
    return Matrix(students, subjects, cells, unexpected)
