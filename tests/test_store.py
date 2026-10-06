import sqlite3

import pytest

REQUIRED_TABLES = {
    "sources", "students", "student_aliases", "subjects", "grading_rules", "raw_records",
    "normalized_records", "evidence", "issues", "decisions", "calculated_scores",
    "final_grades", "audit_logs",
}


def _source(conn):
    conn.execute("INSERT INTO sources (source_id, file_name, file_type, file_sha256, imported_at)"
                 " VALUES ('SRC1', 'a.xlsx', 'xlsx', 'x', 't')")


def test_all_required_tables_exist(conn):
    names = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert REQUIRED_TABLES <= names


def test_raw_records_cannot_be_rewritten(conn):
    _source(conn)
    conn.execute("INSERT INTO raw_records (source_id, cell, original_value) VALUES ('SRC1', 'H32', '85')")
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        conn.execute("UPDATE raw_records SET original_value = '90'")
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        conn.execute("DELETE FROM raw_records")


def test_audit_logs_cannot_be_deleted(conn):
    conn.execute("INSERT INTO audit_logs (timestamp, process, status) VALUES ('t', 'p', 'CONFIRMED')")
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        conn.execute("DELETE FROM audit_logs")


def test_rule_without_source_or_decision_is_rejected(conn):
    conn.execute("INSERT INTO subjects (subject_id, name) VALUES ('AI', 'AI基礎')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO grading_rules (rule_id, subject_id, rule_type, definition)"
                     " VALUES ('R1', 'AI', 'weight', '{}')")


@pytest.mark.parametrize("match_status", ["LIKELY", "AMBIGUOUS", "UNMATCHED"])
@pytest.mark.parametrize("status", ["CONFIRMED", "WARNING"])
def test_unconfirmed_identity_cannot_become_usable(conn, match_status, status):
    _source(conn)
    raw_id = conn.execute("INSERT INTO raw_records (source_id, original_value) VALUES ('SRC1', '85')").lastrowid
    with pytest.raises(sqlite3.DatabaseError, match="must be BLOCKED"):
        conn.execute("INSERT INTO normalized_records (raw_id, match_status, value_kind, status)"
                     " VALUES (?, ?, 'NUMBER', ?)", (raw_id, match_status, status))


def test_final_grade_over_100_is_rejected(conn):
    conn.execute("INSERT INTO subjects (subject_id, name) VALUES ('AI', 'AI基礎')")
    conn.execute("INSERT INTO students (student_key, name, normalized_name) VALUES ('S1', '田中 太郎', '田中太郎')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO final_grades VALUES ('S1', 'AI', 105, 'A', 'R1', 'CONFIRMED')")
