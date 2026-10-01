import json
import sqlite3
from typing import Any

from grading import audit
from grading.clock import now
from grading.decisions import find_decision
from grading.domain.enums import DataStatus, IssueType, Stage


def raise_issue(
    conn: sqlite3.Connection,
    *,
    run_id: str,
    stage: Stage,
    issue_type: IssueType,
    fingerprint: str,
    severity: DataStatus,
    detail: dict[str, Any],
    question: str | None = None,
    priority: int = 100,
) -> int:
    """問題を登録する。同じ問題に過去の回答があれば、その回答で解決済みとして登録する。"""
    if severity == DataStatus.CONFIRMED:
        raise ValueError("CONFIRMED is not an issue")
    if severity == DataStatus.BLOCKED and not question:
        raise ValueError("BLOCKED issue needs a concrete question for the user")
    prior = find_decision(conn, fingerprint)
    cur = conn.execute(
        "INSERT INTO issues (run_id, stage, issue_type, issue_fingerprint, severity, priority, detail, question,"
        " decision_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (run_id, stage, issue_type, fingerprint, severity, priority,
         json.dumps(detail, ensure_ascii=False), question, prior["decision_id"] if prior else None, now()),
    )
    audit.record(conn, run_id=run_id, process=f"issue:{stage}", input=detail,
                 output={"issue_type": issue_type, "reused_decision": prior is not None}, status=severity)
    return cur.lastrowid


def open_blockers(conn: sqlite3.Connection, run_id: str) -> list[sqlite3.Row]:
    """回答待ちの BLOCKED を、先に聞くべき順に返す。"""
    return conn.execute(
        "SELECT * FROM issues WHERE run_id = ? AND severity = 'BLOCKED' AND decision_id IS NULL"
        " ORDER BY priority, issue_id",
        (run_id,),
    ).fetchall()
