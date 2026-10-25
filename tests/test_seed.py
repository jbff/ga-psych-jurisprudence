"""Unit tests for question pool population and distractor generation engine."""

from pathlib import Path
import re
import sqlite3
import pytest

from gamb_exam.seed import (
    OFFICIAL_DOMAINS,
    normalize_text,
    parse_anki_tsv,
    build_question_records,
    seed_database,
)
from gamb_exam.db import get_connection


def test_normalize_text():
    """Test text normalization preserves trailing 's' while cleaning punctuation."""
    assert normalize_text("Yes") == "yes"
    assert normalize_text("witness") == "witness"
    assert normalize_text("class;") == "class"
    assert normalize_text("  hello, world.  ") == "hello, world"
    assert normalize_text("No.") == "no"
    assert normalize_text("  40 credits,  ") == "40 credits"


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


def test_card_425_fine():
    """Test that Card 425 fine is properly set to $500.00."""
    cards = parse_anki_tsv()
    card_425 = next(
        (c for c in cards if "43-1-19" in c["source_citation"] and "civil fine" in c["front"].lower()),
        None,
    )
    assert card_425 is not None, "Card 425 not found in parsed deck"
    assert "$500.00" in card_425["answer_text"], (
        f"Card 425 answer should contain '$500.00', got: {card_425['answer_text']}"
    )


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
        cleaned_opts = [opt.strip().rstrip(".;:!?,").lower() for opt in opts]
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
            selected_option_text.strip().rstrip(".;:!?,").lower()
            == q["answer_text"].strip().rstrip(".;:!?,").lower()
        ), f"Question {i} correct option text '{selected_option_text}' does not match answer '{q['answer_text']}'"

    # Key distribution should be reasonably uniform (~25% each across 435 questions)
    # 435 / 4 = 108.75. Each should be between 80 and 140.
    for key, count in key_counts.items():
        assert (
            80 <= count <= 140
        ), f"Key distribution unbalanced for {key}: count={count} out of 435"


def test_quantitative_no_distractors():
    """Verify quantitative questions like 'No more than three' do not get polar Yes/No distractors."""
    questions = build_question_records()
    polar_prefixes = ("yes,", "yes;", "yes.", "no,", "no;", "no.", "only with", "only if", "only when")

    for q in questions:
        stem = q["question_text"]
        ans = q["answer_text"].lower()

        # Questions that are quantitative or start with 'How many' or have 'No more/less than'
        is_quantitative = (
            stem.lower().startswith("how many")
            or stem.lower().startswith("how often")
            or "no more than" in ans
            or "no less than" in ans
            or ans.startswith("no civil liability")
        )

        if is_quantitative:
            for opt_key in ("option_a", "option_b", "option_c", "option_d"):
                opt = q[opt_key].strip().lower()
                for prefix in polar_prefixes:
                    assert not opt.startswith(prefix), (
                        f"Quantitative question '{stem}' option '{opt}' inappropriately received polar distractor '{prefix}'"
                    )


def test_grammatical_agreement_years():
    """Verify singular/plural grammatical agreement for years in options."""
    questions = build_question_records()

    for q in questions:
        for opt_key in ("option_a", "option_b", "option_c", "option_d"):
            opt = q[opt_key]
            # Must not contain "1 years" or "one years"
            assert not re.search(r"\b(1|one)\s+years\b", opt, re.IGNORECASE), (
                f"Question option '{opt}' has ungrammatical '1 years' or 'one years'"
            )
            # Must not contain "2 year " or "two year " (where number > 1 has singular year)
            assert not re.search(r"\b([2-9]|two|three|four|five|six|seven|eight|nine|ten)\s+year\b", opt, re.IGNORECASE), (
                f"Question option '{opt}' has ungrammatical 'X year' (singular for plural count)"
            )


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


def test_seed_database_idempotency(tmp_path: Path):
    """Test re-seeding the database resets question IDs starting at 1."""
    tmp_db = tmp_path / "gamb_exam_idempotent.db"

    count1 = seed_database(db_path=tmp_db)
    assert count1 == 435

    conn = get_connection(tmp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM questions")
    min_id, max_id, total = cursor.fetchone()
    assert (min_id, max_id, total) == (1, 435, 435)
    conn.close()

    # Re-seed on the same database file
    count2 = seed_database(db_path=tmp_db)
    assert count2 == 435

    conn2 = get_connection(tmp_db)
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM questions")
    min_id2, max_id2, total2 = cursor2.fetchone()
    assert (min_id2, max_id2, total2) == (1, 435, 435), (
        f"Re-seeding failed to reset sequence: got min={min_id2}, max={max_id2}, total={total2}"
    )
    conn2.close()
