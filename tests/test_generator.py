"""Unit tests for the stratified 50-question exam generator and markdown exporter."""

import random
from pathlib import Path

import pytest

from gamb_exam.db import (
    DEFAULT_DB_PATH,
    create_session,
    get_connection,
    get_question_by_id,
    save_session_answer,
)
from gamb_exam.generator import (
    DOMAIN_QUOTAS,
    PASSING_PERCENT,
    PASSING_SCORE,
    TOTAL_QUESTIONS,
    export_mock_markdown,
    generate_exam_questions,
)
from gamb_exam.seed import seed_database


def test_generate_exam_questions_exact_quotas():
    """Generates an exam from data/gamb_exam.db and verifies exact quotas and uniqueness."""
    questions = generate_exam_questions(db_path=DEFAULT_DB_PATH)
    assert len(questions) == TOTAL_QUESTIONS
    assert len(questions) == 50
    assert PASSING_SCORE == 38
    assert PASSING_PERCENT == 76.0

    # Exact domain quotas
    domain_counts: dict[str, int] = {}
    for q in questions:
        domain = q["domain"]
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    assert domain_counts.get("prof-relationships") == 14
    assert domain_counts.get("licensure") == 13
    assert domain_counts.get("competence") == 9
    assert domain_counts.get("assessment") == 6
    assert domain_counts.get("privacy") == 5
    assert domain_counts.get("recordkeeping") == 3

    for domain, quota in DOMAIN_QUOTAS.items():
        assert domain_counts[domain] == quota

    # All 50 questions have unique IDs (no duplicates)
    ids = [q["id"] for q in questions]
    assert len(set(ids)) == 50


def test_option_shuffling():
    """Verifies that when shuffle_options=True, the correct option text matches original."""
    questions = generate_exam_questions(db_path=DEFAULT_DB_PATH, shuffle_options=True)
    assert len(questions) == 50

    for q in questions:
        original = get_question_by_id(q["id"], db_path=DEFAULT_DB_PATH)
        assert original is not None

        orig_correct_key = original["correct_option"].strip().upper()
        orig_correct_text = original[f"option_{orig_correct_key.lower()}"]

        shuffled_correct_key = q["correct_option"].strip().upper()
        shuffled_correct_text = q[f"option_{shuffled_correct_key.lower()}"]

        assert shuffled_correct_text == orig_correct_text

        # All four options must be a permutation of the original options
        orig_opts = sorted([original["option_a"], original["option_b"], original["option_c"], original["option_d"]])
        shuffled_opts = sorted([q["option_a"], q["option_b"], q["option_c"], q["option_d"]])
        assert orig_opts == shuffled_opts


def test_shuffle_options_false():
    """Verifies that shuffle_options=False preserves original options and correct key."""
    questions = generate_exam_questions(db_path=DEFAULT_DB_PATH, shuffle_options=False)
    for q in questions:
        orig = get_question_by_id(q["id"], db_path=DEFAULT_DB_PATH)
        assert orig is not None
        assert q["correct_option"] == orig["correct_option"]
        assert q["option_a"] == orig["option_a"]
        assert q["option_b"] == orig["option_b"]
        assert q["option_c"] == orig["option_c"]
        assert q["option_d"] == orig["option_d"]


def test_prioritize_unseen(tmp_db_path: Path):
    """Verifies prioritize_unseen=True prioritizes questions with fewest prior answers and default is False."""
    seed_database(tmp_db_path)

    # Inspect questions in 'recordkeeping' domain (quota = 3, total = 21)
    conn = get_connection(tmp_db_path)
    cur = conn.cursor()
    cur.execute("SELECT id FROM questions WHERE domain = 'recordkeeping' ORDER BY id ASC")
    recordkeeping_ids = [row["id"] for row in cur.fetchall()]
    conn.close()

    assert len(recordkeeping_ids) >= 3

    # Mark all but 2 of the recordkeeping questions as answered
    unseen_ids = set(recordkeeping_ids[:2])
    seen_ids = recordkeeping_ids[2:]

    session_id = create_session(db_path=tmp_db_path)
    for qid in seen_ids:
        save_session_answer(
            session_id=session_id,
            question_id=qid,
            selected_option="A",
            is_correct=True,
            db_path=tmp_db_path,
        )

    # Default generate_exam_questions has prioritize_unseen=False
    default_questions = generate_exam_questions(db_path=tmp_db_path)
    assert len(default_questions) == 50

    # Explicitly generate exam questions with prioritize_unseen=True
    questions = generate_exam_questions(db_path=tmp_db_path, prioritize_unseen=True)
    generated_rk_ids = {q["id"] for q in questions if q["domain"] == "recordkeeping"}

    # Both unseen questions MUST be prioritized into the 3 selected questions
    assert len(generated_rk_ids) == 3
    assert unseen_ids.issubset(generated_rk_ids)


def test_export_mock_markdown(tmp_path: Path):
    """Verifies mock exam markdown export generates valid questions and key files."""
    questions = generate_exam_questions(db_path=DEFAULT_DB_PATH)
    questions_path, key_path = export_mock_markdown(questions, output_dir=tmp_path)

    assert questions_path.is_file()
    assert key_path.is_file()
    assert questions_path.name == "mock_questions.md"
    assert key_path.name == "mock_key.md"

    q_content = questions_path.read_text(encoding="utf-8")
    k_content = key_path.read_text(encoding="utf-8")

    # Questions file contains instructions, cutoff, disclaimer
    assert "60 minutes" in q_content
    assert "50" in q_content
    assert "38" in q_content
    assert "LEGAL" in q_content
    assert "DISCLAIMER" in q_content

    # Questions file contains all 50 question texts and 4 options
    for q in questions:
        assert q["question_text"] in q_content
        assert q["option_a"] in q_content
        assert q["option_b"] in q_content
        assert q["option_c"] in q_content
        assert q["option_d"] in q_content

    # Key file contains all 50 correct options, citations, and explanations
    assert "Domain Score Worksheet" in k_content
    for q in questions:
        assert q["source_citation"] in k_content
        assert q["explanation"] in k_content
        assert q["correct_option"] in k_content


def test_export_mock_markdown_with_custom_id(tmp_path: Path):
    """Verifies mock_id parameter formats filenames properly."""
    questions = generate_exam_questions(db_path=DEFAULT_DB_PATH)
    q_path, k_path = export_mock_markdown(questions, output_dir=tmp_path, mock_id=1)
    assert q_path.name == "mock1_questions.md"
    assert k_path.name == "mock1_key.md"


def test_rng_determinism():
    """Verifies providing an rng produces deterministic question ordering and shuffling."""
    rng1 = random.Random(12345)
    rng2 = random.Random(12345)
    q1 = generate_exam_questions(db_path=DEFAULT_DB_PATH, rng=rng1)
    q2 = generate_exam_questions(db_path=DEFAULT_DB_PATH, rng=rng2)

    assert [q["id"] for q in q1] == [q["id"] for q in q2]
    assert [q["correct_option"] for q in q1] == [q["correct_option"] for q in q2]
    assert [q["option_a"] for q in q1] == [q["option_a"] for q in q2]


def test_export_mock_markdown_invalid_count(tmp_path: Path):
    """Verifies export_mock_markdown raises ValueError if questions count != 50."""
    with pytest.raises(ValueError, match="Expected 50 questions"):
        export_mock_markdown([], output_dir=tmp_path)
