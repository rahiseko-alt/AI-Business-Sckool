import json
import sqlite3
from typing import Any

from grading.clock import now


def _text(value: Any) -> str | None:
    if value is None or isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


def record(
    conn: sqlite3.Connection,
    *,
    process: str,
    status: str,
    run_id: str | None = None,
    student: str | None = None,
    subject: str | None = None,
    input: Any = None,
    output: Any = None,
    rule: str | None = None,
    source: str | None = None,
) -> None:
    conn.execute(
        "INSERT INTO audit_logs (timestamp, run_id, process, student, subject, input, output, rule, source, status)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (now(), run_id, process, student, subject, _text(input), _text(output), rule, source, status),
    )
