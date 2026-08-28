"""SQLite persistence for private local learning progress and mock sessions."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class LearningStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS progress (
                    learner_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'not_started',
                    favorite INTEGER NOT NULL DEFAULT 0,
                    note TEXT NOT NULL DEFAULT '',
                    score INTEGER,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (learner_id, question_id),
                    CHECK (status IN ('not_started', 'learning', 'review', 'mastered')),
                    CHECK (score IS NULL OR (score >= 0 AND score <= 5))
                );

                CREATE TABLE IF NOT EXISTS interview_sessions (
                    id TEXT PRIMARY KEY,
                    learner_id TEXT NOT NULL,
                    template_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    question_ids_json TEXT NOT NULL,
                    current_index INTEGER NOT NULL DEFAULT 0,
                    seed INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    CHECK (status IN ('active', 'completed', 'abandoned'))
                );

                CREATE TABLE IF NOT EXISTS interview_answers (
                    session_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    answer TEXT NOT NULL DEFAULT '',
                    self_score INTEGER,
                    notes TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (session_id, question_id),
                    FOREIGN KEY (session_id) REFERENCES interview_sessions(id)
                        ON DELETE CASCADE,
                    CHECK (self_score IS NULL OR (self_score >= 0 AND self_score <= 5))
                );
                """
            )

    @staticmethod
    def _progress_row(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["favorite"] = bool(item["favorite"])
        return item

    def get_progress(self, learner_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT learner_id, question_id, status, favorite, note, score, updated_at
                FROM progress
                WHERE learner_id = ?
                ORDER BY updated_at DESC, question_id
                """,
                (learner_id,),
            ).fetchall()
        return [self._progress_row(row) for row in rows]

    def get_question_progress(
        self, learner_id: str, question_id: str
    ) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT learner_id, question_id, status, favorite, note, score, updated_at
                FROM progress
                WHERE learner_id = ? AND question_id = ?
                """,
                (learner_id, question_id),
            ).fetchone()
        return self._progress_row(row) if row else None

    def upsert_progress(
        self, learner_id: str, question_id: str, changes: dict[str, Any]
    ) -> dict[str, Any]:
        current = self.get_question_progress(learner_id, question_id) or {
            "status": "not_started",
            "favorite": False,
            "note": "",
            "score": None,
        }
        merged = {**current, **changes}
        updated_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO progress
                    (learner_id, question_id, status, favorite, note, score, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(learner_id, question_id) DO UPDATE SET
                    status = excluded.status,
                    favorite = excluded.favorite,
                    note = excluded.note,
                    score = excluded.score,
                    updated_at = excluded.updated_at
                """,
                (
                    learner_id,
                    question_id,
                    merged["status"],
                    int(merged["favorite"]),
                    merged["note"],
                    merged["score"],
                    updated_at,
                ),
            )
        result = self.get_question_progress(learner_id, question_id)
        assert result is not None
        return result

    def progress_summary(self, learner_id: str) -> dict[str, int]:
        result = {
            "total_touched": 0,
            "not_started": 0,
            "learning": 0,
            "review": 0,
            "mastered": 0,
            "favorites": 0,
        }
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT status, COUNT(*) AS count, SUM(favorite) AS favorites
                FROM progress WHERE learner_id = ? GROUP BY status
                """,
                (learner_id,),
            ).fetchall()
        for row in rows:
            result[row["status"]] = row["count"]
            result["total_touched"] += row["count"]
            result["favorites"] += row["favorites"] or 0
        return result

    def create_session(
        self,
        *,
        session_id: str,
        learner_id: str,
        template_id: str,
        question_ids: list[str],
        seed: int,
    ) -> dict[str, Any]:
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO interview_sessions
                    (id, learner_id, template_id, status, question_ids_json,
                     current_index, seed, created_at, updated_at)
                VALUES (?, ?, ?, 'active', ?, 0, ?, ?, ?)
                """,
                (
                    session_id,
                    learner_id,
                    template_id,
                    json.dumps(question_ids, ensure_ascii=False),
                    seed,
                    now,
                    now,
                ),
            )
        result = self.get_session(session_id)
        assert result is not None
        return result

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM interview_sessions WHERE id = ?", (session_id,)
            ).fetchone()
            answer_rows = connection.execute(
                """
                SELECT question_id, answer, self_score, notes, updated_at
                FROM interview_answers WHERE session_id = ?
                """,
                (session_id,),
            ).fetchall()
        if not row:
            return None
        result = dict(row)
        result["question_ids"] = json.loads(result.pop("question_ids_json"))
        result["answers"] = {
            answer["question_id"]: dict(answer) for answer in answer_rows
        }
        return result

    def save_answer(
        self,
        session_id: str,
        question_id: str,
        *,
        answer: str,
        self_score: int | None,
        notes: str,
        next_index: int,
    ) -> dict[str, Any]:
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO interview_answers
                    (session_id, question_id, answer, self_score, notes, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id, question_id) DO UPDATE SET
                    answer = excluded.answer,
                    self_score = excluded.self_score,
                    notes = excluded.notes,
                    updated_at = excluded.updated_at
                """,
                (session_id, question_id, answer, self_score, notes, now),
            )
            connection.execute(
                """
                UPDATE interview_sessions
                SET current_index = MAX(current_index, ?), updated_at = ?
                WHERE id = ?
                """,
                (next_index, now, session_id),
            )
        result = self.get_session(session_id)
        assert result is not None
        return result

    def update_session_status(self, session_id: str, status: str) -> dict[str, Any]:
        now = utc_now()
        completed_at = now if status == "completed" else None
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE interview_sessions
                SET status = ?, updated_at = ?, completed_at = ?
                WHERE id = ?
                """,
                (status, now, completed_at, session_id),
            )
        result = self.get_session(session_id)
        assert result is not None
        return result
