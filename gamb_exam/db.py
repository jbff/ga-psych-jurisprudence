"""Database engine and persistence layer for the Georgia Jurisprudence Exam Simulator."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path("data/gamb_exam.db")


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Return an SQLite connection configured with row factory and foreign keys.

    Creates parent directories if necessary.
    """
    target_path = DEFAULT_DB_PATH if db_path is None else db_path
    if str(target_path) != ":memory:":
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Path | str | None = None) -> None:
    """Initialize the SQLite database with the required schema and indexes."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    subtopic TEXT,
                    source_citation TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    option_a TEXT NOT NULL,
                    option_b TEXT NOT NULL,
                    option_c TEXT NOT NULL,
                    option_d TEXT NOT NULL,
                    correct_option TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS exam_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode TEXT NOT NULL,
                    total_questions INTEGER NOT NULL DEFAULT 50,
                    score INTEGER,
                    percentage REAL,
                    passed BOOLEAN,
                    time_spent_seconds INTEGER,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS session_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL REFERENCES exam_sessions(id) ON DELETE CASCADE,
                    question_id INTEGER NOT NULL REFERENCES questions(id),
                    selected_option TEXT,
                    is_correct BOOLEAN NOT NULL,
                    flagged BOOLEAN DEFAULT FALSE,
                    time_spent_seconds INTEGER
                );

                CREATE INDEX IF NOT EXISTS idx_questions_domain ON questions(domain);
                CREATE INDEX IF NOT EXISTS idx_session_answers_session ON session_answers(session_id);
                CREATE INDEX IF NOT EXISTS idx_session_answers_question ON session_answers(question_id);
                """
            )
    finally:
        conn.close()


def insert_question(question_dict: dict[str, Any], db_path: Path | str | None = None) -> int:
    """Insert a question into the database and return its primary key ID."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO questions (
                    domain, subtopic, source_citation, question_text,
                    option_a, option_b, option_c, option_d,
                    correct_option, explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    question_dict["domain"],
                    question_dict.get("subtopic"),
                    question_dict["source_citation"],
                    question_dict["question_text"],
                    question_dict["option_a"],
                    question_dict["option_b"],
                    question_dict["option_c"],
                    question_dict["option_d"],
                    question_dict["correct_option"],
                    question_dict["explanation"],
                ),
            )
            return cursor.lastrowid  # type: ignore[return-value]
    finally:
        conn.close()


def get_question_by_id(question_id: int, db_path: Path | str | None = None) -> dict[str, Any] | None:
    """Retrieve a single question by its primary key ID."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
        row = cursor.fetchone()
        return dict(row) if row is not None else None
    finally:
        conn.close()


def get_questions_by_domain(
    domain: str, db_path: Path | str | None = None, limit: int | None = None
) -> list[dict[str, Any]]:
    """Retrieve questions filtered by domain, with an optional limit."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        if limit is not None:
            cursor.execute(
                "SELECT * FROM questions WHERE domain = ? ORDER BY id ASC LIMIT ?",
                (domain, limit),
            )
        else:
            cursor.execute(
                "SELECT * FROM questions WHERE domain = ? ORDER BY id ASC",
                (domain,),
            )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_all_questions(db_path: Path | str | None = None) -> list[dict[str, Any]]:
    """Retrieve all questions from the database."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def create_session(
    mode: str = "timed_exam",
    total_questions: int = 50,
    db_path: Path | str | None = None,
) -> int:
    """Create a new exam session record and return its primary key ID."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO exam_sessions (mode, total_questions) VALUES (?, ?)",
                (mode, total_questions),
            )
            return cursor.lastrowid  # type: ignore[return-value]
    finally:
        conn.close()


def complete_session(
    session_id: int,
    score: int,
    percentage: float,
    passed: bool,
    time_spent_seconds: int,
    db_path: Path | str | None = None,
) -> None:
    """Mark an exam session as completed and update its results."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE exam_sessions
                SET score = ?, percentage = ?, passed = ?, time_spent_seconds = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    score,
                    percentage,
                    int(passed) if isinstance(passed, bool) else passed,
                    time_spent_seconds,
                    session_id,
                ),
            )
    finally:
        conn.close()


def save_session_answer(
    session_id: int,
    question_id: int,
    selected_option: str | None,
    is_correct: bool,
    flagged: bool = False,
    time_spent_seconds: int = 0,
    db_path: Path | str | None = None,
) -> int:
    """Record an answer for a specific question within an exam session."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO session_answers (
                    session_id, question_id, selected_option, is_correct, flagged, time_spent_seconds
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    question_id,
                    selected_option,
                    int(is_correct) if isinstance(is_correct, bool) else is_correct,
                    int(flagged) if isinstance(flagged, bool) else flagged,
                    time_spent_seconds,
                ),
            )
            return cursor.lastrowid  # type: ignore[return-value]
    finally:
        conn.close()


def get_missed_questions(db_path: Path | str | None = None) -> list[dict[str, Any]]:
    """Retrieve distinct questions that were answered incorrectly in any session."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT q.*
            FROM questions q
            JOIN session_answers sa ON q.id = sa.question_id
            WHERE sa.is_correct = 0
            ORDER BY q.id ASC
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_session_history(db_path: Path | str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    """Retrieve exam session history ordered by most recent first."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM exam_sessions
            ORDER BY started_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
