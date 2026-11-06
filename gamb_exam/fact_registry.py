"""Fact Registry module for Georgia Psychology Jurisprudence Examination.

Provides schema definitions, data loader, coverage verification, and
integrity validation for atomic testable facts across Georgia statutes,
Board rules, and PSI testing standards.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FACT_INVENTORY_JSON = PROJECT_ROOT / "data" / "fact_inventory.json"

VALID_DOMAINS: set[str] = {
    "licensure",
    "privacy",
    "prof-relationships",
    "competence",
    "assessment",
    "recordkeeping",
}

VALID_SOURCE_TYPES: set[str] = {
    "OCGA",
    "RULE",
    "PSI_BULLETIN",
}

VALID_AUDIT_STATUSES: set[str] = {
    "verified",
    "draft",
}

REQUIRED_FACT_FIELDS: tuple[str, ...] = (
    "fact_id",
    "source_type",
    "citation",
    "domain",
    "domain_display",
    "subtopic",
    "rule_summary",
    "key_parameters",
    "associated_question_ids",
    "associated_anki_card_ids",
    "audit_status",
)


def load_facts(path: Path | str | None = None) -> list[dict[str, Any]]:
    """Load atomic facts from data/fact_inventory.json or the specified path.

    Args:
        path: Optional custom path to fact_inventory.json.

    Returns:
        A list of dictionary objects representing atomic facts.

    Raises:
        FileNotFoundError: If the fact inventory file does not exist.
        ValueError: If the file contents cannot be parsed as a list of dicts.
    """
    file_path = FACT_INVENTORY_JSON if path is None else Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Fact inventory file not found at {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Fact inventory at {file_path} must be a JSON array, got {type(data).__name__}")

    return data


def save_facts(facts: list[dict[str, Any]], path: Path | str | None = None) -> None:
    """Save atomic facts to data/fact_inventory.json or the specified path.

    Args:
        facts: List of atomic fact dictionaries.
        path: Optional custom path to save the inventory.
    """
    file_path = FACT_INVENTORY_JSON if path is None else Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=2, ensure_ascii=False)
        f.write("\n")


def verify_fact_coverage(
    facts: list[dict[str, Any]],
    check_drafts: bool = False,
) -> list[str]:
    """Verify that every atomic fact is covered by at least one question and one Anki card.

    Draft facts (audit_status == 'draft') represent facts pending question authoring in Task 5
    and are skipped unless check_drafts=True. Verified facts (audit_status == 'verified')
    must have at least one question ID and one Anki card ID.

    Args:
        facts: List of atomic fact dictionaries.
        check_drafts: When True, enforce coverage on draft facts as well.

    Returns:
        A list of error strings identifying uncovered facts (empty if 100% covered).
    """
    errors: list[str] = []
    if not isinstance(facts, list):
        return [f"Fact inventory must be a list, got {type(facts).__name__}"]

    for idx, fact in enumerate(facts):
        if not isinstance(fact, dict):
            errors.append(f"Fact at index {idx} must be a dict, got {type(fact).__name__}")
            continue

        fid = fact.get("fact_id", "<missing fact_id>")
        status = fact.get("audit_status")
        if status == "draft" and not check_drafts:
            continue

        qids = fact.get("associated_question_ids")
        cids = fact.get("associated_anki_card_ids")

        if not isinstance(qids, list) or len(qids) < 1:
            errors.append(f"Fact {fid} has 0 associated questions (requires >= 1).")
        if not isinstance(cids, list) or len(cids) < 1:
            errors.append(f"Fact {fid} has 0 associated anki cards (requires >= 1).")

    return errors


def validate_fact_inventory(
    facts: list[dict[str, Any]],
    question_pool: list[dict[str, Any]] | None = None,
    anki_lines: list[str] | None = None,
) -> list[str]:
    """Validate full schema compliance, uniqueness, coverage, and foreign key references.

    Args:
        facts: List of fact dictionaries to validate.
        question_pool: Optional list of question objects from question_pool.json.
        anki_lines: Optional list of lines from anki/gamb_deck.tsv.

    Returns:
        A list of validation error message strings (empty if valid).
    """
    errors: list[str] = []

    if not isinstance(facts, list):
        return [f"Fact inventory must be a list, got {type(facts).__name__}"]

    seen_ids: set[str] = set()

    for idx, fact in enumerate(facts):
        if not isinstance(fact, dict):
            errors.append(f"Fact at index {idx} must be a dict, got {type(fact).__name__}")
            continue

        fid = fact.get("fact_id")

        # 1. Check required fields
        for field in REQUIRED_FACT_FIELDS:
            if field not in fact:
                errors.append(f"Fact at index {idx} ({fid or 'no-id'}) missing required field '{field}'")

        # 2. Check fact_id uniqueness & non-empty string
        if not isinstance(fid, str) or not fid.strip():
            errors.append(f"Fact at index {idx} has missing or empty 'fact_id'")
        else:
            if fid in seen_ids:
                errors.append(f"Duplicate fact_id '{fid}' detected at index {idx}")
            seen_ids.add(fid)

        # 3. Check source_type
        stype = fact.get("source_type")
        if stype not in VALID_SOURCE_TYPES:
            errors.append(
                f"Fact {fid} has invalid source_type '{stype}' (allowed: {sorted(VALID_SOURCE_TYPES)})"
            )

        # 4. Check citation
        citation = fact.get("citation")
        if not isinstance(citation, str) or not citation.strip():
            errors.append(f"Fact {fid} citation must be a non-empty string")

        # 5. Check domain slug
        domain = fact.get("domain")
        if domain not in VALID_DOMAINS:
            errors.append(
                f"Fact {fid} domain '{domain}' is invalid (allowed slugs: {sorted(VALID_DOMAINS)})"
            )

        # 6. Check domain_display
        domain_display = fact.get("domain_display")
        if not isinstance(domain_display, str) or not domain_display.strip():
            errors.append(f"Fact {fid} domain_display must be a non-empty string")

        # 7. Check subtopic
        subtopic = fact.get("subtopic")
        if not isinstance(subtopic, str) or not subtopic.strip():
            errors.append(f"Fact {fid} subtopic must be a non-empty string")

        # 8. Check rule_summary
        rule_summary = fact.get("rule_summary")
        if not isinstance(rule_summary, str) or not rule_summary.strip():
            errors.append(f"Fact {fid} rule_summary must be a non-empty string")

        # 9. Check key_parameters
        key_parameters = fact.get("key_parameters")
        if not isinstance(key_parameters, dict):
            errors.append(f"Fact {fid} key_parameters must be a dict")

        # 10. Check associated_question_ids
        qids = fact.get("associated_question_ids")
        if not isinstance(qids, list):
            errors.append(f"Fact {fid} associated_question_ids must be a list of integers")
        elif not all(isinstance(q, int) and q >= 1 for q in qids):
            errors.append(f"Fact {fid} associated_question_ids must contain only positive integers")

        # 11. Check associated_anki_card_ids
        cids = fact.get("associated_anki_card_ids")
        if not isinstance(cids, list):
            errors.append(f"Fact {fid} associated_anki_card_ids must be a list of integers")
        elif not all(isinstance(c, int) and c >= 1 for c in cids):
            errors.append(f"Fact {fid} associated_anki_card_ids must contain only positive integers")

        # 12. Check audit_status
        status = fact.get("audit_status")
        if status not in VALID_AUDIT_STATUSES:
            errors.append(
                f"Fact {fid} audit_status '{status}' is invalid (allowed: {sorted(VALID_AUDIT_STATUSES)})"
            )

    # 13. Fact coverage validation
    errors.extend(verify_fact_coverage(facts))

    # 14. Question pool foreign key validation
    if question_pool is not None:
        valid_qids = {
            q["id"]
            for q in question_pool
            if isinstance(q, dict) and isinstance(q.get("id"), int)
        }
        for fact in facts:
            if not isinstance(fact, dict):
                continue
            fid = fact.get("fact_id", "<unknown>")
            qids = fact.get("associated_question_ids")
            if isinstance(qids, list):
                for qid in qids:
                    if qid not in valid_qids:
                        errors.append(
                            f"Fact {fid} references question_id {qid} not found in question_pool"
                        )

    # 15. Anki TSV foreign key validation
    if anki_lines is not None:
        card_count = sum(
            1 for line in anki_lines if line.strip() and not line.startswith("#")
        )
        for fact in facts:
            if not isinstance(fact, dict):
                continue
            fid = fact.get("fact_id", "<unknown>")
            cids = fact.get("associated_anki_card_ids")
            if isinstance(cids, list):
                for cid in cids:
                    if not (1 <= cid <= card_count):
                        errors.append(
                            f"Fact {fid} references anki card_id {cid} outside valid range (1..{card_count})"
                        )

    return errors
