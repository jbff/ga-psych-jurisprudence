"""Automated validation suite for Georgia Jurisprudence atomic fact inventory.

Validates schema compliance, domain taxonomies, unique identifiers,
100% coverage across the question pool and Anki deck, and cross-reference integrity.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gamb_exam.fact_registry import (
    FACT_INVENTORY_JSON,
    REQUIRED_FACT_FIELDS,
    VALID_AUDIT_STATUSES,
    VALID_DOMAINS,
    VALID_SOURCE_TYPES,
    load_facts,
    validate_fact_inventory,
    verify_fact_coverage,
)
from gamb_exam.seed import DEFAULT_TSV_PATH, QUESTION_POOL_JSON


@pytest.fixture(scope="module")
def facts() -> list[dict]:
    """Load the atomic fact inventory."""
    return load_facts()


@pytest.fixture(scope="module")
def question_pool() -> list[dict]:
    """Load question_pool.json."""
    assert QUESTION_POOL_JSON.exists(), f"Question pool file not found: {QUESTION_POOL_JSON}"
    with open(QUESTION_POOL_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    return data


@pytest.fixture(scope="module")
def anki_lines() -> list[str]:
    """Load raw lines from anki/gamb_deck.tsv."""
    assert DEFAULT_TSV_PATH.exists(), f"Anki TSV file not found: {DEFAULT_TSV_PATH}"
    with open(DEFAULT_TSV_PATH, "r", encoding="utf-8") as f:
        return f.readlines()


def test_fact_inventory_file_exists():
    """Verify data/fact_inventory.json exists and is non-empty."""
    assert FACT_INVENTORY_JSON.exists(), f"Fact inventory file not found at {FACT_INVENTORY_JSON}"
    with open(FACT_INVENTORY_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list), "data/fact_inventory.json must be a JSON array"
    assert len(data) >= 1, "data/fact_inventory.json must contain at least 1 fact"


def test_fact_schema(facts: list[dict]):
    """Every fact must adhere to the required schema and field constraints.

    Required fields:
    - fact_id: non-empty string
    - source_type: one of ('OCGA', 'RULE', 'PSI_BULLETIN')
    - citation: non-empty string
    - domain: valid domain slug in VALID_DOMAINS
    - domain_display: non-empty string
    - subtopic: non-empty string
    - rule_summary: non-empty string
    - key_parameters: dict
    - associated_question_ids: list of int
    - associated_anki_card_ids: list of int
    - audit_status: one of ('verified', 'draft')
    """
    assert len(facts) >= 1, "Fact inventory is empty"

    for idx, fact in enumerate(facts):
        # 1. Required keys presence
        for field in REQUIRED_FACT_FIELDS:
            assert field in fact, f"Fact at index {idx} missing required field '{field}'"

        # 2. Field types and non-empty checks
        assert isinstance(fact["fact_id"], str) and fact["fact_id"].strip(), (
            f"Fact at index {idx} has invalid fact_id: {fact.get('fact_id')}"
        )
        assert fact["source_type"] in VALID_SOURCE_TYPES, (
            f"Fact {fact['fact_id']} has invalid source_type '{fact['source_type']}' "
            f"(must be one of {VALID_SOURCE_TYPES})"
        )
        assert isinstance(fact["citation"], str) and fact["citation"].strip(), (
            f"Fact {fact['fact_id']} citation must be a non-empty string"
        )
        assert fact["domain"] in VALID_DOMAINS, (
            f"Fact {fact['fact_id']} domain '{fact['domain']}' not in {VALID_DOMAINS}"
        )
        assert isinstance(fact["domain_display"], str) and fact["domain_display"].strip(), (
            f"Fact {fact['fact_id']} domain_display must be a non-empty string"
        )
        assert isinstance(fact["subtopic"], str) and fact["subtopic"].strip(), (
            f"Fact {fact['fact_id']} subtopic must be a non-empty string"
        )
        assert isinstance(fact["rule_summary"], str) and fact["rule_summary"].strip(), (
            f"Fact {fact['fact_id']} rule_summary must be a non-empty string"
        )
        assert isinstance(fact["key_parameters"], dict), (
            f"Fact {fact['fact_id']} key_parameters must be a dict"
        )
        assert isinstance(fact["associated_question_ids"], list), (
            f"Fact {fact['fact_id']} associated_question_ids must be a list"
        )
        assert all(isinstance(qid, int) and qid >= 1 for qid in fact["associated_question_ids"]), (
            f"Fact {fact['fact_id']} associated_question_ids must all be positive integers"
        )
        assert isinstance(fact["associated_anki_card_ids"], list), (
            f"Fact {fact['fact_id']} associated_anki_card_ids must be a list"
        )
        assert all(isinstance(cid, int) and cid >= 1 for cid in fact["associated_anki_card_ids"]), (
            f"Fact {fact['fact_id']} associated_anki_card_ids must all be positive integers"
        )
        assert fact["audit_status"] in VALID_AUDIT_STATUSES, (
            f"Fact {fact['fact_id']} audit_status '{fact['audit_status']}' not in {VALID_AUDIT_STATUSES}"
        )


def test_domain_slugs_valid(facts: list[dict]):
    """Domains strictly match the 6 official machine slugs."""
    expected_slugs = {
        "licensure",
        "privacy",
        "prof-relationships",
        "competence",
        "assessment",
        "recordkeeping",
    }
    assert VALID_DOMAINS == expected_slugs
    for fact in facts:
        assert fact["domain"] in expected_slugs, (
            f"Fact {fact.get('fact_id')} has invalid domain: {fact.get('domain')}"
        )


def test_100_percent_fact_coverage(facts: list[dict]):
    """Asserts that len(fact['associated_question_ids']) >= 1 and len(fact['associated_anki_card_ids']) >= 1 for every fact."""
    errors = verify_fact_coverage(facts)
    assert not errors, f"Uncovered facts found:\n" + "\n".join(errors)


def test_unique_fact_ids(facts: list[dict]):
    """No duplicate fact_id strings across the inventory."""
    seen_ids: set[str] = set()
    duplicates: list[str] = []
    for fact in facts:
        fid = fact.get("fact_id")
        if fid in seen_ids:
            duplicates.append(fid)
        seen_ids.add(fid)
    assert not duplicates, f"Duplicate fact_ids detected: {duplicates}"


def test_validate_fact_inventory_helper(
    facts: list[dict],
    question_pool: list[dict],
    anki_lines: list[str],
):
    """The full validation helper validate_fact_inventory returns no errors on valid inventory."""
    errors = validate_fact_inventory(facts, question_pool=question_pool, anki_lines=anki_lines)
    assert not errors, f"Validation errors reported:\n" + "\n".join(errors)


def test_validate_fact_inventory_catches_invalid_domain():
    """validate_fact_inventory detects invalid domain slug."""
    bad_fact = [
        {
            "fact_id": "FACT-TEST-001",
            "source_type": "RULE",
            "citation": "Rule 510-1",
            "domain": "invalid-domain",
            "domain_display": "Invalid Domain",
            "subtopic": "test",
            "rule_summary": "Test summary",
            "key_parameters": {},
            "associated_question_ids": [1],
            "associated_anki_card_ids": [1],
            "audit_status": "verified",
        }
    ]
    errors = validate_fact_inventory(bad_fact)
    assert any("domain" in err for err in errors), f"Expected domain error, got {errors}"


def test_validate_fact_inventory_catches_duplicate_ids():
    """validate_fact_inventory detects duplicate fact_id entries."""
    duplicate_facts = [
        {
            "fact_id": "FACT-DUP-001",
            "source_type": "RULE",
            "citation": "Rule 510-1",
            "domain": "licensure",
            "domain_display": "Licensure",
            "subtopic": "test",
            "rule_summary": "Test summary 1",
            "key_parameters": {},
            "associated_question_ids": [1],
            "associated_anki_card_ids": [1],
            "audit_status": "verified",
        },
        {
            "fact_id": "FACT-DUP-001",
            "source_type": "OCGA",
            "citation": "OCGA 43-39-1",
            "domain": "licensure",
            "domain_display": "Licensure",
            "subtopic": "test",
            "rule_summary": "Test summary 2",
            "key_parameters": {},
            "associated_question_ids": [1],
            "associated_anki_card_ids": [1],
            "audit_status": "verified",
        },
    ]
    errors = validate_fact_inventory(duplicate_facts)
    assert any("Duplicate fact_id" in err for err in errors), f"Expected duplicate error, got {errors}"


def test_verify_fact_coverage_catches_uncovered_facts():
    """verify_fact_coverage flags facts with empty associated questions or cards."""
    uncovered_facts = [
        {
            "fact_id": "FACT-NO-Q-001",
            "source_type": "RULE",
            "citation": "Rule 510-1",
            "domain": "licensure",
            "domain_display": "Licensure",
            "subtopic": "test",
            "rule_summary": "Test summary",
            "key_parameters": {},
            "associated_question_ids": [],
            "associated_anki_card_ids": [1],
            "audit_status": "verified",
        },
        {
            "fact_id": "FACT-NO-ANKI-002",
            "source_type": "RULE",
            "citation": "Rule 510-1",
            "domain": "licensure",
            "domain_display": "Licensure",
            "subtopic": "test",
            "rule_summary": "Test summary",
            "key_parameters": {},
            "associated_question_ids": [1],
            "associated_anki_card_ids": [],
            "audit_status": "verified",
        },
    ]
    errors = verify_fact_coverage(uncovered_facts)
    assert len(errors) == 2
    assert any("FACT-NO-Q-001" in err and "question" in err for err in errors)
    assert any("FACT-NO-ANKI-002" in err and "anki" in err for err in errors)


def test_validate_fact_inventory_catches_invalid_foreign_keys(question_pool: list[dict], anki_lines: list[str]):
    """validate_fact_inventory flags associated IDs that do not exist in question pool or Anki deck."""
    bad_fk_fact = [
        {
            "fact_id": "FACT-BAD-FK",
            "source_type": "RULE",
            "citation": "Rule 510-1",
            "domain": "licensure",
            "domain_display": "Licensure",
            "subtopic": "test",
            "rule_summary": "Test summary",
            "key_parameters": {},
            "associated_question_ids": [99999],
            "associated_anki_card_ids": [99999],
            "audit_status": "verified",
        }
    ]
    errors = validate_fact_inventory(bad_fk_fact, question_pool=question_pool, anki_lines=anki_lines)
    assert any("99999" in err and "question_pool" in err for err in errors)
    assert any("99999" in err and "anki" in err for err in errors)


def test_load_facts_nonexistent_file(tmp_path: Path):
    """load_facts raises FileNotFoundError when given non-existent path."""
    non_existent = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        load_facts(non_existent)


def test_save_and_load_facts_roundtrip(tmp_path: Path, facts: list[dict]):
    """save_facts and load_facts correctly preserve fact structure across round-trip."""
    from gamb_exam.fact_registry import save_facts

    custom_path = tmp_path / "test_inventory.json"
    save_facts(facts, custom_path)
    loaded = load_facts(custom_path)
    assert loaded == facts


def test_validate_and_verify_malformed_facts(question_pool: list[dict], anki_lines: list[str]):
    """validate_fact_inventory and verify_fact_coverage handle malformed facts cleanly without crashing."""
    malformed_facts = [
        "not-a-dict",
        {
            "fact_id": "FACT-MALFORMED-001",
            "source_type": "RULE",
            "citation": "Rule 510-1",
            "domain": "licensure",
            "domain_display": "Licensure",
            "subtopic": "test",
            "rule_summary": "Test summary",
            "key_parameters": {},
            "associated_question_ids": None,
            "associated_anki_card_ids": None,
            "audit_status": "verified",
        },
    ]

    cov_errors = verify_fact_coverage(malformed_facts)  # type: ignore[arg-type]
    assert any("must be a dict" in err for err in cov_errors)
    assert any("FACT-MALFORMED-001" in err and "question" in err for err in cov_errors)
    assert any("FACT-MALFORMED-001" in err and "anki" in err for err in cov_errors)

    val_errors = validate_fact_inventory(
        malformed_facts,  # type: ignore[arg-type]
        question_pool=question_pool,
        anki_lines=anki_lines,
    )
    assert any("must be a dict" in err for err in val_errors)
    assert any("associated_question_ids" in err for err in val_errors)
    assert any("associated_anki_card_ids" in err for err in val_errors)

    # Test non-list input handling
    non_list_cov = verify_fact_coverage("not-a-list")  # type: ignore[arg-type]
    assert any("must be a list" in err for err in non_list_cov)
    non_list_val = validate_fact_inventory("not-a-list")  # type: ignore[arg-type]
    assert any("must be a list" in err for err in non_list_val)



