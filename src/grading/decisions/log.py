import json
import sqlite3
import uuid
from typing import Any

from grading import audit
from grading.clock import now


def find_decision(conn: sqlite3.Connection, fingerprint: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM decisions WHERE issue_fingerprint = ?", (fingerprint,)).fetchone()


def record_decision(
    conn: sqlite3.Connection,
    *,
    issue_id: int,
    user_answer: str,
    resolved_value: Any,
    affected_records: list[Any] | None = None,
) -> str:
    """回答を保存し、同じ問題の未解決 issue をすべて解決済みにする。"""
    issue = conn.execute("SELECT * FROM issues WHERE issue_id = ?", (issue_id,)).fetchone()
    if issue is None:
        raise KeyError(issue_id)
    if find_decision(conn, issue["issue_fingerprint"]) is not None:
        raise ValueError("this issue was already answered")
    decision_id = f"D{uuid.uuid4().hex[:12]}"
    conn.execute(
        "INSERT INTO decisions (decision_id, issue_type, issue_fingerprint, source, question, user_answer,"
        " resolved_value, timestamp, affected_records) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (decision_id, issue["issue_type"], issue["issue_fingerprint"], issue["detail"], issue["question"],
         user_answer, json.dumps(resolved_value, ensure_ascii=False), now(),
         json.dumps(affected_records or [], ensure_ascii=False)),
    )
    conn.execute(
        "UPDATE issues SET decision_id = ? WHERE issue_fingerprint = ? AND decision_id IS NULL",
        (decision_id, issue["issue_fingerprint"]),
    )
    audit.record(conn, run_id=issue["run_id"], process="decision", input=user_answer,
                 output=resolved_value, status="CONFIRMED")
    return decision_id
