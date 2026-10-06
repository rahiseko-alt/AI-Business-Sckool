-- 成績統合システムのデータ構造。
-- 段階ごとに表を分け、元の値は書き換えない（raw / evidence / decisions / audit_logs は追記専用）。
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id         TEXT PRIMARY KEY,
    current_stage  TEXT NOT NULL,
    held_stage     TEXT,            -- ASK_USER で止まったとき、再開先の工程
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    source_id    TEXT PRIMARY KEY,
    file_name    TEXT NOT NULL,
    file_type    TEXT NOT NULL,
    sheet_name   TEXT,
    page         INTEGER,
    subject      TEXT,
    class        TEXT,
    period       TEXT,
    role         TEXT,              -- 未確定なら NULL
    file_sha256  TEXT NOT NULL,     -- 取込後に元資料が変わっていないかの確認用
    imported_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    student_key      TEXT PRIMARY KEY,   -- 内部ID（例: S00123）
    student_number   TEXT UNIQUE,        -- 学籍番号
    name             TEXT NOT NULL,
    normalized_name  TEXT NOT NULL,
    class            TEXT,
    seat_number      INTEGER,
    email            TEXT,
    school_id        TEXT
);

CREATE TABLE IF NOT EXISTS student_aliases (
    alias_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    student_key      TEXT NOT NULL REFERENCES students(student_key),
    original_name    TEXT NOT NULL,
    normalized_name  TEXT NOT NULL,
    source_id        TEXT REFERENCES sources(source_id),
    decision_id      TEXT REFERENCES decisions(decision_id)
);

CREATE TABLE IF NOT EXISTS subjects (
    subject_id  TEXT PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE
);

-- 科目ごとに独立。別科目のルールを参照する列は持たない。
CREATE TABLE IF NOT EXISTS grading_rules (
    rule_id      TEXT PRIMARY KEY,
    subject_id   TEXT NOT NULL REFERENCES subjects(subject_id),
    rule_type    TEXT NOT NULL,     -- weight / grade_band / max_score / missing_policy 等
    item         TEXT,
    definition   TEXT NOT NULL,     -- JSON
    source_id    TEXT REFERENCES sources(source_id),
    decision_id  TEXT REFERENCES decisions(decision_id),
    CHECK (source_id IS NOT NULL OR decision_id IS NOT NULL)   -- 根拠の無いルールは登録不可
);

CREATE TABLE IF NOT EXISTS raw_records (
    raw_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id       TEXT NOT NULL REFERENCES sources(source_id),
    sheet_name      TEXT,
    cell            TEXT,
    page            INTEGER,
    row_number      INTEGER,
    column_label    TEXT,
    original_value  TEXT            -- 原文のまま（NULL は本当に空のセル）
);

CREATE TABLE IF NOT EXISTS normalized_records (
    norm_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_id            INTEGER NOT NULL REFERENCES raw_records(raw_id),
    student_key       TEXT REFERENCES students(student_key),
    match_status      TEXT NOT NULL,
    subject_id        TEXT REFERENCES subjects(subject_id),
    item              TEXT,
    value_kind        TEXT NOT NULL,
    normalized_value  REAL,
    corrected_value   REAL,
    correction_reason TEXT,
    decision_id       TEXT REFERENCES decisions(decision_id),
    status            TEXT NOT NULL CHECK (status IN ('CONFIRMED','WARNING','BLOCKED')),
    CHECK (corrected_value IS NULL OR decision_id IS NOT NULL)   -- 修正は必ず回答に紐づける
);

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    student_key       TEXT REFERENCES students(student_key),
    subject_id        TEXT REFERENCES subjects(subject_id),
    item              TEXT,
    value             REAL,
    raw_id            INTEGER NOT NULL REFERENCES raw_records(raw_id),
    source_id         TEXT NOT NULL REFERENCES sources(source_id),
    file_name         TEXT NOT NULL,
    sheet_name        TEXT,
    cell              TEXT,
    page              INTEGER,
    row_number        INTEGER,
    original_value    TEXT,
    normalized_value  TEXT
);

CREATE TABLE IF NOT EXISTS decisions (
    decision_id       TEXT PRIMARY KEY,
    issue_type        TEXT NOT NULL,
    issue_fingerprint TEXT NOT NULL UNIQUE,  -- 同じ問題を二度聞かないための鍵
    source            TEXT,
    question          TEXT NOT NULL,
    user_answer       TEXT NOT NULL,
    resolved_value    TEXT NOT NULL,
    timestamp         TEXT NOT NULL,
    affected_records  TEXT                   -- JSON
);

CREATE TABLE IF NOT EXISTS issues (
    issue_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id            TEXT NOT NULL REFERENCES pipeline_runs(run_id),
    stage             TEXT NOT NULL,
    issue_type        TEXT NOT NULL,
    issue_fingerprint TEXT NOT NULL,
    severity          TEXT NOT NULL CHECK (severity IN ('WARNING','BLOCKED')),
    priority          INTEGER NOT NULL DEFAULT 100,  -- 小さいほど先に聞く（学生特定が最優先）
    detail            TEXT NOT NULL,                  -- JSON: 資料・行・セル・候補
    question          TEXT,
    decision_id       TEXT REFERENCES decisions(decision_id),
    created_at        TEXT NOT NULL,
    UNIQUE (run_id, issue_fingerprint)
);

CREATE TABLE IF NOT EXISTS calculated_scores (
    calc_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    student_key   TEXT NOT NULL REFERENCES students(student_key),
    subject_id    TEXT NOT NULL REFERENCES subjects(subject_id),
    item          TEXT NOT NULL,
    score         REAL NOT NULL,
    rule_id       TEXT NOT NULL REFERENCES grading_rules(rule_id),
    evidence_ids  TEXT NOT NULL      -- JSON 配列。根拠の無い得点は作らない
);

CREATE TABLE IF NOT EXISTS final_grades (
    student_key   TEXT NOT NULL REFERENCES students(student_key),
    subject_id    TEXT NOT NULL REFERENCES subjects(subject_id),
    total_score   REAL NOT NULL CHECK (total_score >= 0 AND total_score <= 100),
    grade         TEXT NOT NULL,
    rule_id       TEXT NOT NULL REFERENCES grading_rules(rule_id),
    status        TEXT NOT NULL CHECK (status IN ('CONFIRMED','WARNING','BLOCKED')),
    PRIMARY KEY (student_key, subject_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp  TEXT NOT NULL,
    run_id     TEXT,
    process    TEXT NOT NULL,
    student    TEXT,
    subject    TEXT,
    input      TEXT,
    output     TEXT,
    rule       TEXT,
    source     TEXT,
    status     TEXT NOT NULL
);

-- 追記専用の表は、更新・削除をデータベース自身が拒否する
CREATE TRIGGER IF NOT EXISTS raw_records_no_update BEFORE UPDATE ON raw_records
BEGIN SELECT RAISE(ABORT, 'raw_records is append-only'); END;
CREATE TRIGGER IF NOT EXISTS raw_records_no_delete BEFORE DELETE ON raw_records
BEGIN SELECT RAISE(ABORT, 'raw_records is append-only'); END;
CREATE TRIGGER IF NOT EXISTS evidence_no_update BEFORE UPDATE ON evidence
BEGIN SELECT RAISE(ABORT, 'evidence is append-only'); END;
CREATE TRIGGER IF NOT EXISTS evidence_no_delete BEFORE DELETE ON evidence
BEGIN SELECT RAISE(ABORT, 'evidence is append-only'); END;
CREATE TRIGGER IF NOT EXISTS decisions_no_update BEFORE UPDATE ON decisions
BEGIN SELECT RAISE(ABORT, 'decisions is append-only'); END;
CREATE TRIGGER IF NOT EXISTS decisions_no_delete BEFORE DELETE ON decisions
BEGIN SELECT RAISE(ABORT, 'decisions is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_logs_no_update BEFORE UPDATE ON audit_logs
BEGIN SELECT RAISE(ABORT, 'audit_logs is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_logs_no_delete BEFORE DELETE ON audit_logs
BEGIN SELECT RAISE(ABORT, 'audit_logs is append-only'); END;

-- LIKELY / AMBIGUOUS / UNMATCHED の名寄せは CONFIRMED / WARNING の確定値にできない
CREATE TRIGGER IF NOT EXISTS normalized_unconfirmed_identity_is_blocked
BEFORE INSERT ON normalized_records
WHEN NEW.match_status <> 'CONFIRMED' AND NEW.status <> 'BLOCKED'
BEGIN SELECT RAISE(ABORT, 'unconfirmed identity must be BLOCKED'); END;
