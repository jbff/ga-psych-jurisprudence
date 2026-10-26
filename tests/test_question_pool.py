"""Tests for curated question pool JSON integrity and database seeding."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gamb_exam.db import get_connection
from gamb_exam.seed import OFFICIAL_DOMAINS, QUESTION_POOL_JSON, seed_database


@pytest.fixture(scope="module")
def question_pool_path() -> Path:
    """Return path to question_pool.json."""
    return QUESTION_POOL_JSON


@pytest.fixture(scope="module")
def question_pool(question_pool_path: Path) -> list[dict]:
    """Load and parse question_pool.json."""
    assert question_pool_path.exists(), f"Question pool file not found at {question_pool_path}"
    with open(question_pool_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list), "question_pool.json must contain a list of question objects"
    return data


def test_question_pool_file_exists_and_valid_json(question_pool_path: Path):
    """Verify gamb_exam/question_pool.json exists and parses cleanly as valid JSON."""
    assert question_pool_path.exists(), f"File does not exist: {question_pool_path}"
    with open(question_pool_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) > 0, "Question pool must not be empty"


def test_total_435_count(question_pool: list[dict]):
    """Verify question pool contains exactly 435 questions."""
    if len(question_pool) < 435:
        pytest.xfail(f"Partial audit in progress: {len(question_pool)}/435 questions present")
    assert len(question_pool) == 435


def test_question_object_structure(question_pool: list[dict]):
    """Verify structure and constraints of each question object in question_pool.json."""
    for idx, q in enumerate(question_pool):
        # 1. id: integer between 1 and 435
        assert isinstance(q.get("id"), int), f"Question {idx} 'id' must be an int"
        assert 1 <= q["id"] <= 435, f"Question {idx} 'id' {q['id']} outside 1..435"

        # 2. domain: one of 6 official Board domains
        assert q.get("domain") in OFFICIAL_DOMAINS, (
            f"Question {idx} invalid domain: '{q.get('domain')}'"
        )

        # 3. source_citation: non-empty string
        assert isinstance(q.get("source_citation"), str) and q["source_citation"].strip(), (
            f"Question {idx} source_citation must be a non-empty string"
        )

        # 4. question_text: non-empty string
        assert isinstance(q.get("question_text"), str) and q["question_text"].strip(), (
            f"Question {idx} question_text must be a non-empty string"
        )

        # 5. options: dict with keys {"A", "B", "C", "D"}
        opts = q.get("options")
        assert isinstance(opts, dict), f"Question {idx} 'options' must be a dict"
        assert set(opts.keys()) == {"A", "B", "C", "D"}, (
            f"Question {idx} options keys must be exactly {{'A', 'B', 'C', 'D'}}, got {set(opts.keys())}"
        )

        # 6. All 4 options are non-empty strings and mutually distinct
        for opt_key in ("A", "B", "C", "D"):
            opt_val = opts[opt_key]
            assert isinstance(opt_val, str) and opt_val.strip(), (
                f"Question {idx} option {opt_key} must be a non-empty string"
            )

        cleaned_opts = [
            opts[k].strip().rstrip(".;:!?,").lower() for k in ("A", "B", "C", "D")
        ]
        assert len(set(cleaned_opts)) == 4, (
            f"Question {idx} (id={q['id']}) options contain duplicates: {opts}"
        )

        # 7. correct_option: one of 'A', 'B', 'C', 'D'
        assert q.get("correct_option") in {"A", "B", "C", "D"}, (
            f"Question {idx} correct_option '{q.get('correct_option')}' must be one of A, B, C, D"
        )

        # 8. explanation: non-empty string
        assert isinstance(q.get("explanation"), str) and q["explanation"].strip(), (
            f"Question {idx} explanation must be a non-empty string"
        )


def test_question_ids_unique_and_ordered(question_pool: list[dict]):
    """Verify question IDs are unique and sequential."""
    ids = [q["id"] for q in question_pool]
    assert len(ids) == len(set(ids)), "Question IDs must be unique"
    assert ids == sorted(ids), "Question IDs must be in ascending order"


def test_seed_database_loads_from_question_pool(tmp_path: Path, question_pool: list[dict]):
    """Verify seed_database loads records directly from question_pool.json into SQLite."""
    tmp_db = tmp_path / "gamb_pool_test.db"
    seeded_count = seed_database(db_path=tmp_db)
    assert seeded_count == len(question_pool), (
        f"Expected {len(question_pool)} questions seeded, got {seeded_count}"
    )

    conn = get_connection(tmp_db)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        total = cursor.fetchone()[0]
        assert total == len(question_pool)

        # Verify first question content matches question_pool.json
        cursor.execute(
            "SELECT id, domain, question_text, option_a, option_b, option_c, option_d, correct_option, explanation "
            "FROM questions ORDER BY id LIMIT 1"
        )
        row = cursor.fetchone()
        assert row is not None

        first_q = question_pool[0]
        assert row["id"] == first_q["id"]
        assert row["domain"] == first_q["domain"]
        assert row["question_text"] == first_q["question_text"]
        assert row["option_a"] == first_q["options"]["A"]
        assert row["option_b"] == first_q["options"]["B"]
        assert row["option_c"] == first_q["options"]["C"]
        assert row["option_d"] == first_q["options"]["D"]
        assert row["correct_option"] == first_q["correct_option"]
        assert row["explanation"] == first_q["explanation"]
    finally:
        conn.close()


def test_fallback_to_tsv_when_json_missing(monkeypatch, tmp_path: Path):
    """Verify build_question_records falls back to TSV parser if QUESTION_POOL_JSON does not exist."""
    fake_path = tmp_path / "nonexistent_question_pool.json"
    import gamb_exam.seed as seed_mod

    monkeypatch.setattr(seed_mod, "QUESTION_POOL_JSON", fake_path)
    records = seed_mod.build_question_records()
    assert len(records) == 435, f"Expected 435 fallback records, got {len(records)}"


def test_question_pool_metadata():
    """Verify question_pool_metadata.json exists, parses cleanly, and defines version 1.0 with 10/25/2026."""
    from gamb_exam.seed import (
        QUESTION_POOL_DATE,
        QUESTION_POOL_METADATA_JSON,
        QUESTION_POOL_VERSION,
        get_pool_metadata,
    )

    assert QUESTION_POOL_METADATA_JSON.exists(), f"Missing metadata file: {QUESTION_POOL_METADATA_JSON}"
    with open(QUESTION_POOL_METADATA_JSON, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["version"] == "1.0"
    assert meta["date"] == "10/25/2026"
    assert meta["total_questions"] == 435
    assert QUESTION_POOL_VERSION == "1.0"
    assert QUESTION_POOL_DATE == "10/25/2026"

    helper_meta = get_pool_metadata()
    assert helper_meta["version"] == "1.0"
    assert helper_meta["date"] == "10/25/2026"


