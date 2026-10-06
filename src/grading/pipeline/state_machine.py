"""LOAD → … → EXPORT の状態遷移。

各工程の処理が終わったら advance() を呼ぶ。未解決の BLOCKED があれば次へ進まず
ASK_USER で止まり、すべて回答されたら resume() で止まった工程から再実行する。
"""

import sqlite3
import uuid

from grading import audit
from grading.clock import now
from grading.domain.enums import Stage
from grading.issues import open_blockers

ORDER: list[Stage] = [
    Stage.LOAD,
    Stage.CLASSIFY,
    Stage.EXTRACT,
    Stage.IDENTITY_RESOLUTION,
    Stage.RULE_BINDING,
    Stage.CALCULATE,
    Stage.VALIDATE,
    Stage.MERGE,
    Stage.FINAL_CHECK,
    Stage.EXPORT,
    Stage.DONE,
]


class PipelineHalted(RuntimeError):
    """回答待ちのまま先へ進もうとした。"""


class Pipeline:
    def __init__(self, conn: sqlite3.Connection, run_id: str | None = None):
        self.conn = conn
        if run_id is None:
            run_id = f"R{uuid.uuid4().hex[:12]}"
            conn.execute(
                "INSERT INTO pipeline_runs (run_id, current_stage, held_stage, created_at, updated_at)"
                " VALUES (?, ?, NULL, ?, ?)",
                (run_id, Stage.LOAD, now(), now()),
            )
            audit.record(conn, run_id=run_id, process="pipeline:start", output=Stage.LOAD, status="CONFIRMED")
        elif conn.execute("SELECT 1 FROM pipeline_runs WHERE run_id = ?", (run_id,)).fetchone() is None:
            raise KeyError(run_id)
        self.run_id = run_id

    @property
    def stage(self) -> Stage:
        row = self.conn.execute("SELECT current_stage FROM pipeline_runs WHERE run_id = ?", (self.run_id,)).fetchone()
        return Stage(row["current_stage"])

    @property
    def held_stage(self) -> Stage | None:
        row = self.conn.execute("SELECT held_stage FROM pipeline_runs WHERE run_id = ?", (self.run_id,)).fetchone()
        return Stage(row["held_stage"]) if row["held_stage"] else None

    def advance(self) -> Stage:
        """現工程を終えて次へ。BLOCKED が残っていれば ASK_USER で止まる。"""
        current = self.stage
        if current == Stage.ASK_USER:
            raise PipelineHalted("waiting for user answers; call resume() after answering")
        if current == Stage.DONE:
            raise PipelineHalted("pipeline already finished")
        blockers = open_blockers(self.conn, self.run_id)
        if blockers:
            self._set(Stage.ASK_USER, held=current)
            audit.record(self.conn, run_id=self.run_id, process=f"pipeline:{current}",
                         output={"halted": [b["issue_id"] for b in blockers]}, status="BLOCKED")
            return Stage.ASK_USER
        nxt = ORDER[ORDER.index(current) + 1]
        self._set(nxt, held=None)
        audit.record(self.conn, run_id=self.run_id, process=f"pipeline:{current}", output=nxt, status="CONFIRMED")
        return nxt

    def resume(self) -> Stage:
        """すべての BLOCKED に回答済みなら、止まった工程へ戻って再実行する。"""
        if self.stage != Stage.ASK_USER:
            raise PipelineHalted("not waiting for user")
        if open_blockers(self.conn, self.run_id):
            raise PipelineHalted("unanswered BLOCKED issues remain")
        held = self.held_stage
        self._set(held, held=None)
        audit.record(self.conn, run_id=self.run_id, process="pipeline:resume", output=held, status="CONFIRMED")
        return held

    def _set(self, stage: Stage, *, held: Stage | None) -> None:
        self.conn.execute(
            "UPDATE pipeline_runs SET current_stage = ?, held_stage = ?, updated_at = ? WHERE run_id = ?",
            (stage, held, now(), self.run_id),
        )
