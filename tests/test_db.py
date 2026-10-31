"""Unit tests for gamb_exam database engine and CRUD operations."""

import sqlite3
from pathlib import Path

import pytest

from gamb_exam.db import (
    complete_session,
    create_session,
    get_all_questions,
    get_connection,
    get_last_wrong_questions,
    get_missed_questions,
    get_question_by_id,
    get_questions_by_domain,
    get_session_history,
    get_study_progress,
    init_db,
    insert_question,
    insert_questions,
    save_session_answer,
)


def sample_question_data(domain: str = "prof-relationships", stem_suffix: str = "1") -> dict:
    """Helper to generate sample question dict."""
    return {
        "domain": domain,
        "subtopic": "dual-relationships",
        "source_citation": "Board Rule 510-4-.01",
        "question_text": f"What is the rule regarding dual relationships in scenario {stem_suffix}?",
        "option_a": "Never engage in them",
        "option_b": "Allowed anytime with informed consent",
        "option_c": "Allowed only after 2 years",
        "option_d": "Allowed if fee is refunded",
        "correct_option": "A",
        "explanation": "Board Rule 510-4-.01 strictly prohibits harmful dual relationships.",
    }


def test_init_db(tmp_db_path: Path):
    """Verifies init_db creates tables questions, exam_sessions, session_answers."""
    init_db(tmp_db_path)

    conn = get_connection(tmp_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row["name"] for row in cursor.fetchall()}
    conn.close()

    assert "questions" in tables
    assert "exam_sessions" in tables
    assert "session_answers" in tables


def test_insert_and_fetch_question(tmp_db_path: Path):
    """Verifies inserting questions and retrieving by id, domain, or all."""
    init_db(tmp_db_path)

    q1_data = sample_question_data(domain="prof-relationships", stem_suffix="A")
    q2_data = sample_question_data(domain="licensure", stem_suffix="B")
    q3_data = sample_question_data(domain="prof-relationships", stem_suffix="C")

    qid1 = insert_question(q1_data, db_path=tmp_db_path)
    qid2 = insert_question(q2_data, db_path=tmp_db_path)
    qid3 = insert_question(q3_data, db_path=tmp_db_path)

    assert isinstance(qid1, int)
    assert isinstance(qid2, int)
    assert qid2 > qid1

    # Fetch by ID
    fetched_q1 = get_question_by_id(qid1, db_path=tmp_db_path)
    assert fetched_q1 is not None
    assert fetched_q1["id"] == qid1
    assert fetched_q1["domain"] == "prof-relationships"
    assert fetched_q1["question_text"] == q1_data["question_text"]
    assert fetched_q1["correct_option"] == "A"
    assert fetched_q1["explanation"] == q1_data["explanation"]

    # Non-existent ID returns None
    assert get_question_by_id(99999, db_path=tmp_db_path) is None

    # Fetch by domain
    prof_questions = get_questions_by_domain("prof-relationships", db_path=tmp_db_path)
    assert len(prof_questions) == 2
    assert {q["id"] for q in prof_questions} == {qid1, qid3}

    # Fetch by domain with limit
    limited_prof = get_questions_by_domain("prof-relationships", db_path=tmp_db_path, limit=1)
    assert len(limited_prof) == 1

    # Fetch all questions
    all_questions = get_all_questions(db_path=tmp_db_path)
    assert len(all_questions) == 3


def test_bulk_insert_questions(tmp_db_path: Path):
    """Verifies batch insertion of questions via insert_questions."""
    init_db(tmp_db_path)

    # Empty batch returns 0
    assert insert_questions([], db_path=tmp_db_path) == 0
    assert len(get_all_questions(db_path=tmp_db_path)) == 0

    batch = [
        sample_question_data(domain="competence", stem_suffix=f"batch_{i}")
        for i in range(5)
    ]
    count = insert_questions(batch, db_path=tmp_db_path)
    assert count == 5

    stored = get_all_questions(db_path=tmp_db_path)
    assert len(stored) == 5
    assert [q["question_text"] for q in stored] == [q["question_text"] for q in batch]


def test_session_lifecycle(tmp_db_path: Path):
    """Verifies creating an exam session, recording answers, completing, and fetching history."""
    init_db(tmp_db_path)

    q1_data = sample_question_data(domain="prof-relationships", stem_suffix="1")
    q2_data = sample_question_data(domain="licensure", stem_suffix="2")
    qid1 = insert_question(q1_data, db_path=tmp_db_path)
    qid2 = insert_question(q2_data, db_path=tmp_db_path)

    # 1. Create session
    session_id = create_session(mode="timed_exam", total_questions=2, db_path=tmp_db_path)
    assert isinstance(session_id, int)

    # 2. Record question answers
    ans1_id = save_session_answer(
        session_id=session_id,
        question_id=qid1,
        selected_option="A",
        is_correct=True,
        flagged=False,
        time_spent_seconds=25,
        db_path=tmp_db_path,
    )
    ans2_id = save_session_answer(
        session_id=session_id,
        question_id=qid2,
        selected_option="C",
        is_correct=False,
        flagged=True,
        time_spent_seconds=40,
        db_path=tmp_db_path,
    )
    assert isinstance(ans1_id, int)
    assert isinstance(ans2_id, int)

    # 3. Complete session
    complete_session(
        session_id=session_id,
        score=1,
        percentage=50.0,
        passed=False,
        time_spent_seconds=65,
        db_path=tmp_db_path,
    )

    # 4. Fetch history
    history = get_session_history(db_path=tmp_db_path)
    assert len(history) == 1
    session_record = history[0]
    assert session_record["id"] == session_id
    assert session_record["mode"] == "timed_exam"
    assert session_record["total_questions"] == 2
    assert session_record["score"] == 1
    assert session_record["percentage"] == 50.0
    assert session_record["passed"] == 0 or session_record["passed"] is False
    assert session_record["time_spent_seconds"] == 65
    assert session_record["completed_at"] is not None


def test_get_missed_questions(tmp_db_path: Path):
    """Verifies querying questions that were answered incorrectly in previous sessions."""
    init_db(tmp_db_path)

    q1_data = sample_question_data(domain="competence", stem_suffix="Q1")
    q2_data = sample_question_data(domain="assessment", stem_suffix="Q2")
    q3_data = sample_question_data(domain="privacy", stem_suffix="Q3")

    qid1 = insert_question(q1_data, db_path=tmp_db_path)
    qid2 = insert_question(q2_data, db_path=tmp_db_path)
    qid3 = insert_question(q3_data, db_path=tmp_db_path)

    session1 = create_session(mode="study_drill", total_questions=3, db_path=tmp_db_path)
    # Q1 correct, Q2 wrong
    save_session_answer(session1, qid1, "A", is_correct=True, db_path=tmp_db_path)
    save_session_answer(session1, qid2, "B", is_correct=False, db_path=tmp_db_path)

    session2 = create_session(mode="timed_exam", total_questions=2, db_path=tmp_db_path)
    # Q2 wrong again, Q3 wrong
    save_session_answer(session2, qid2, "C", is_correct=False, db_path=tmp_db_path)
    save_session_answer(session2, qid3, "B", is_correct=False, db_path=tmp_db_path)

    missed = get_missed_questions(db_path=tmp_db_path)
    missed_ids = [q["id"] for q in missed]

    # Q2 and Q3 should be in missed, but Q2 should appear only once (distinct)
    assert len(missed) == 2
    assert set(missed_ids) == {qid2, qid3}

    # Session 3: candidate gets Q2 right on second attempt
    session3 = create_session(mode="study_drill", total_questions=1, db_path=tmp_db_path)
    save_session_answer(session3, qid2, "A", is_correct=True, db_path=tmp_db_path)

    # Q2 should graduate out; now only Q3 remains in missed pool
    updated_missed = get_missed_questions(db_path=tmp_db_path)
    assert len(updated_missed) == 1
    assert updated_missed[0]["id"] == qid3


def test_foreign_key_enforcement(tmp_db_path: Path):
    """Verifies SQLite foreign key constraints are enforced."""
    init_db(tmp_db_path)

    # Attempting to save session answer with non-existent session_id must fail
    with pytest.raises(sqlite3.IntegrityError):
        save_session_answer(
            session_id=999,
            question_id=1,
            selected_option="A",
            is_correct=True,
            db_path=tmp_db_path,
        )


def test_default_db_path(tmp_path: Path, monkeypatch):
    """Verifies DEFAULT_DB_PATH directory creation when db_path=None."""
    mock_db = tmp_path / "data_dir" / "mock.db"
    monkeypatch.setattr("gamb_exam.db.DEFAULT_DB_PATH", mock_db)

    conn = get_connection()
    assert mock_db.exists()
    conn.close()


def test_ensure_db_initialized(tmp_path: Path):
    """Verifies ensure_db_initialized initializes schema and seeds questions on demand."""
    from gamb_exam.db import ensure_db_initialized, get_all_questions

    test_db = tmp_path / "auto_seed.db"
    assert not test_db.exists()

    # First call: creates and seeds database
    seeded = ensure_db_initialized(test_db)
    assert seeded is True
    assert test_db.exists()
    questions = get_all_questions(test_db)
    assert len(questions) == 435

    # Second call: idempotent, already initialized
    seeded_again = ensure_db_initialized(test_db)
    assert seeded_again is False


def test_get_study_questions_unseen_prioritization(tmp_db_path: Path):
    """Verifies get_study_questions prioritizes questions with zero answers before answered ones."""
    init_db(tmp_db_path)
    # Insert 4 questions in prof-relationships
    for i in range(1, 5):
        insert_question(
            sample_question_data(domain="prof-relationships", stem_suffix=str(i)),
            db_path=tmp_db_path,
        )

    # Answer questions 1 and 2
    sess_id = create_session(db_path=tmp_db_path)
    save_session_answer(session_id=sess_id, question_id=1, selected_option="A", is_correct=True, db_path=tmp_db_path)
    save_session_answer(session_id=sess_id, question_id=2, selected_option="B", is_correct=False, db_path=tmp_db_path)

    # Retrieve 2 questions with prioritize_unseen=True
    from gamb_exam.db import get_study_questions

    study_qs = get_study_questions(domain="prof-relationships", limit=2, prioritize_unseen=True, db_path=tmp_db_path)
    assert len(study_qs) == 2
    # Questions 3 and 4 have 0 answers, so both must be selected
    study_ids = {q["id"] for q in study_qs}
    assert study_ids == {3, 4}


def test_get_study_questions_backfill_and_no_unseen(tmp_db_path: Path):
    """Verifies graceful backfill when count exceeds unseen and verify prioritize_unseen=False."""
    init_db(tmp_db_path)
    for i in range(1, 4):
        insert_question(
            sample_question_data(domain="licensure", stem_suffix=str(i)),
            db_path=tmp_db_path,
        )

    # Question 1 answered twice, question 2 answered once, question 3 answered zero times
    sess_id = create_session(db_path=tmp_db_path)
    save_session_answer(session_id=sess_id, question_id=1, selected_option="A", is_correct=True, db_path=tmp_db_path)
    save_session_answer(session_id=sess_id, question_id=1, selected_option="A", is_correct=True, db_path=tmp_db_path)
    save_session_answer(session_id=sess_id, question_id=2, selected_option="A", is_correct=True, db_path=tmp_db_path)

    from gamb_exam.db import get_study_questions

    # Request all 3: order must be question 3 (0 answers), then question 2 (1 answer), then question 1 (2 answers)
    study_qs = get_study_questions(domain="licensure", limit=3, prioritize_unseen=True, db_path=tmp_db_path)
    assert [q["id"] for q in study_qs] == [3, 2, 1]

    # Test prioritize_unseen=False returns all questions without errors
    random_qs = get_study_questions(domain=None, limit=3, prioritize_unseen=False, db_path=tmp_db_path)
    assert len(random_qs) == 3


def test_get_study_progress(tmp_db_path: Path):
    """Aggregates seen/clean/ever-wrong item counts per domain, ignoring skips."""
    init_db(tmp_db_path)

    q1 = insert_question(sample_question_data("competence", "Q1"), db_path=tmp_db_path)
    q2 = insert_question(sample_question_data("competence", "Q2"), db_path=tmp_db_path)
    q3 = insert_question(sample_question_data("assessment", "Q3"), db_path=tmp_db_path)
    q4 = insert_question(sample_question_data("assessment", "Q4"), db_path=tmp_db_path)
    insert_question(sample_question_data("privacy", "Q5"), db_path=tmp_db_path)
    q6 = insert_question(sample_question_data("privacy", "Q6"), db_path=tmp_db_path)

    s1 = create_session(mode="study_drill", total_questions=5, db_path=tmp_db_path)
    save_session_answer(s1, q1, "A", is_correct=True, db_path=tmp_db_path)
    save_session_answer(s1, q2, "B", is_correct=False, db_path=tmp_db_path)
    save_session_answer(s1, q3, None, is_correct=False, db_path=tmp_db_path)
    save_session_answer(s1, q4, "A", is_correct=True, db_path=tmp_db_path)
    save_session_answer(s1, q6, None, is_correct=False, db_path=tmp_db_path)

    s2 = create_session(mode="timed_exam", total_questions=2, db_path=tmp_db_path)
    save_session_answer(s2, q2, "A", is_correct=True, db_path=tmp_db_path)
    save_session_answer(s2, q3, "C", is_correct=False, db_path=tmp_db_path)

    progress = {row["domain"]: row for row in get_study_progress(db_path=tmp_db_path)}

    comp = progress["competence"]
    assert comp["total_items"] == 2
    assert comp["seen_items"] == 2
    assert comp["clean_items"] == 1
    assert comp["ever_wrong_items"] == 1

    assess = progress["assessment"]
    assert assess["total_items"] == 2
    assert assess["seen_items"] == 2
    assert assess["clean_items"] == 1
    assert assess["ever_wrong_items"] == 1

    privacy = progress["privacy"]
    assert privacy["total_items"] == 2
    assert privacy["seen_items"] == 0
    assert privacy["clean_items"] == 0
    assert privacy["ever_wrong_items"] == 0


def test_get_last_wrong_questions(tmp_db_path: Path):
    """Returns questions whose most recent answered attempt was wrong, ignoring skips."""
    init_db(tmp_db_path)

    q1 = insert_question(sample_question_data("competence", "Q1"), db_path=tmp_db_path)
    q2 = insert_question(sample_question_data("assessment", "Q2"), db_path=tmp_db_path)
    q3 = insert_question(sample_question_data("privacy", "Q3"), db_path=tmp_db_path)
    q4 = insert_question(sample_question_data("recordkeeping", "Q4"), db_path=tmp_db_path)
    q5 = insert_question(sample_question_data("licensure", "Q5"), db_path=tmp_db_path)

    s1 = create_session(mode="study_drill", total_questions=5, db_path=tmp_db_path)
    save_session_answer(s1, q1, "B", is_correct=False, db_path=tmp_db_path)
    save_session_answer(s1, q2, "B", is_correct=False, db_path=tmp_db_path)
    save_session_answer(s1, q3, None, is_correct=False, db_path=tmp_db_path)
    save_session_answer(s1, q4, "D", is_correct=False, db_path=tmp_db_path)
    save_session_answer(s1, q5, "A", is_correct=True, db_path=tmp_db_path)

    s2 = create_session(mode="timed_exam", total_questions=3, db_path=tmp_db_path)
    save_session_answer(s2, q1, "A", is_correct=True, db_path=tmp_db_path)
    save_session_answer(s2, q2, None, is_correct=False, db_path=tmp_db_path)
    save_session_answer(s2, q5, None, is_correct=False, db_path=tmp_db_path)

    missed = get_last_wrong_questions(db_path=tmp_db_path)

    # q1 graduated out (last answered correct); q3 never answered;
    # q5's later skip does not count as its last answered attempt.
    assert [q["id"] for q in missed] == [q2, q4]
    assert missed[0]["question_text"] == "What is the rule regarding dual relationships in scenario Q2?"

