"""Unit tests for question pool population and distractor generation engine."""

from pathlib import Path
import sqlite3
import pytest

from gamb_exam.seed import (
    OFFICIAL_DOMAINS,
    parse_anki_tsv,
    build_question_records,
    seed_database,
)
from gamb_exam.db import get_connection


def test_parse_anki_cards():
    """Test reading anki/gamb_deck.tsv yields 435 cards with valid fields."""
    cards = parse_anki_tsv()
    assert len(cards) == 435, f"Expected 435 cards, got {len(cards)}"

    for i, card in enumerate(cards):
        assert card["front"].strip(), f"Card {i} front must be non-empty"
        assert card["back"].strip(), f"Card {i} back must be non-empty"
        assert card["answer_text"].strip(), f"Card {i} answer_text must be non-empty"
        assert card["source_citation"].strip(), f"Card {i} source_citation must be non-empty"
        assert (
            card["domain"] in OFFICIAL_DOMAINS
        ), f"Card {i} domain '{card['domain']}' not in official domains"


def test_question_record_structure():
    """Test that every card converted into a question record has 4 distinct options and valid keys."""
    questions = build_question_records()
    assert len(questions) == 435, f"Expected 435 questions, got {len(questions)}"

    key_counts = {"A": 0, "B": 0, "C": 0, "D": 0}

    for i, q in enumerate(questions):
        # Domain validation
        assert (
            q["domain"] in OFFICIAL_DOMAINS
        ), f"Question {i} domain '{q['domain']}' invalid"

        # Non-empty text fields
        assert q["question_text"].strip(), f"Question {i} question_text empty"
        assert q["source_citation"].strip(), f"Question {i} source_citation empty"
        assert q["explanation"].strip(), f"Question {i} explanation empty"

        # 4 options presence and non-empty
        opts = [q["option_a"], q["option_b"], q["option_c"], q["option_d"]]
        for opt_idx, opt in enumerate(opts):
            letter = chr(ord("A") + opt_idx)
            assert isinstance(opt, str) and opt.strip(), f"Question {i} option_{letter.lower()} is empty"

        # All 4 options must be distinct (stripping trailing punctuation and whitespace)
        cleaned_opts = [opt.strip().rstrip(".;:!?").lower() for opt in opts]
        assert (
            len(set(cleaned_opts)) == 4
        ), f"Question {i} options contain duplicates: {opts} (cleaned: {cleaned_opts})"

        # correct_option validation
        correct_key = q["correct_option"]
        assert correct_key in {
            "A",
            "B",
            "C",
            "D",
        }, f"Question {i} invalid correct_option '{correct_key}'"
        key_counts[correct_key] += 1

        # Correct option text matches answer text
        selected_option_text = q[f"option_{correct_key.lower()}"]
        assert (
            selected_option_text.strip().rstrip(".;:!?").lower()
            == q["answer_text"].strip().rstrip(".;:!?").lower()
        ), f"Question {i} correct option text '{selected_option_text}' does not match answer '{q['answer_text']}'"

    # Key distribution should be reasonably uniform (~25% each across 435 questions)
    # 435 / 4 = 108.75. Each should be between 80 and 140.
    for key, count in key_counts.items():
        assert (
            80 <= count <= 140
        ), f"Key distribution unbalanced for {key}: count={count} out of 435"


def test_seed_database(tmp_path: Path):
    """Test calling seed_database inserts 435 questions with expected domain distribution."""
    tmp_db = tmp_path / "gamb_exam_test.db"
    seeded_count = seed_database(db_path=tmp_db)
    assert seeded_count == 435, f"Expected 435 seeded questions, got {seeded_count}"

    conn = get_connection(tmp_db)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        total = cursor.fetchone()[0]
        assert total == 435

        cursor.execute("SELECT domain, COUNT(*) FROM questions GROUP BY domain")
        domain_counts = dict(cursor.fetchall())

        expected_distribution = {
            "prof-relationships": 73,
            "licensure": 185,
            "competence": 104,
            "assessment": 30,
            "privacy": 22,
            "recordkeeping": 21,
        }
        assert domain_counts == expected_distribution, (
            f"Domain distribution mismatch: got {domain_counts}, "
            f"expected {expected_distribution}"
        )
    finally:
        conn.close()
