import pytest

from grading.decisions import record_decision
from grading.domain.enums import DataStatus, IssueType, Stage
from grading.issues import open_blockers, raise_issue
from grading.pipeline import Pipeline, PipelineHalted
from grading.pipeline.state_machine import ORDER


def _block(conn, p, fingerprint="identity:src1:row32"):
    return raise_issue(
        conn, run_id=p.run_id, stage=p.stage, issue_type=IssueType.IDENTITY_AMBIGUOUS,
        fingerprint=fingerprint, severity=DataStatus.BLOCKED,
        detail={"file": "AI課題一覧.xlsx", "row": 32, "name": "田中 太郎"},
        question="「田中 太郎」は A(20260031/1A) と B(20260082/1B) のどちらですか？", priority=1,
    )


def test_runs_through_all_stages_in_order_when_nothing_is_blocked(conn):
    p = Pipeline(conn)
    seen = [p.stage]
    while p.stage != Stage.DONE:
        seen.append(p.advance())
    assert seen == ORDER


def test_blocked_issue_halts_and_resumes_at_same_stage(conn):
    p = Pipeline(conn)
    for _ in range(3):
        p.advance()
    assert p.stage == Stage.IDENTITY_RESOLUTION
    issue_id = _block(conn, p)

    assert p.advance() == Stage.ASK_USER
    with pytest.raises(PipelineHalted):
        p.advance()
    with pytest.raises(PipelineHalted):
        p.resume()

    record_decision(conn, issue_id=issue_id, user_answer="A", resolved_value={"student_key": "S00123"})
    assert p.resume() == Stage.IDENTITY_RESOLUTION
    assert p.advance() == Stage.RULE_BINDING


def test_warning_does_not_halt(conn):
    p = Pipeline(conn)
    raise_issue(conn, run_id=p.run_id, stage=p.stage, issue_type=IssueType.IDENTITY_AMBIGUOUS,
                fingerprint="w", severity=DataStatus.WARNING, detail={"note": "全角半角のみ違う"})
    assert p.advance() == Stage.CLASSIFY


def test_blocked_issue_requires_a_question(conn):
    p = Pipeline(conn)
    with pytest.raises(ValueError):
        raise_issue(conn, run_id=p.run_id, stage=p.stage, issue_type=IssueType.RULE_UNKNOWN,
                    fingerprint="r", severity=DataStatus.BLOCKED, detail={})


def test_answered_issue_is_not_asked_again_in_a_later_run(conn):
    first = Pipeline(conn)
    record_decision(conn, issue_id=_block(conn, first), user_answer="A", resolved_value={"student_key": "S00123"})

    second = Pipeline(conn)
    _block(conn, second)
    assert open_blockers(conn, second.run_id) == []


def test_pipeline_can_be_reloaded_from_db(conn):
    p = Pipeline(conn)
    p.advance()
    assert Pipeline(conn, p.run_id).stage == Stage.CLASSIFY
