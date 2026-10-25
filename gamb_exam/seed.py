"""Question pool population and distractor generation engine.

Parses Georgia Jurisprudence Anki flashcards (anki/gamb_deck.tsv),
transforms cards into 4-choice multiple choice question records with
legally plausible distractors and code citations, and seeds data/gamb_exam.db.
"""

from __future__ import annotations

import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from gamb_exam.db import (
    DEFAULT_DB_PATH,
    get_connection,
    init_db,
    insert_questions,
)

OFFICIAL_DOMAINS: set[str] = {
    "prof-relationships",
    "licensure",
    "competence",
    "assessment",
    "privacy",
    "recordkeeping",
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TSV_PATH = PROJECT_ROOT / "anki" / "gamb_deck.tsv"

CITATION_REGEX = re.compile(
    r"\(\s*((?:OCGA|Rule|O\.C\.G\.A\.|Board|APA|Code|Ga\.)[^)]*(?:\([^)]*\)[^)]*)*)\)\.?\s*$",
    re.IGNORECASE,
)

ROBUST_FALLBACKS: list[str] = [
    "At the discretion of the psychologist with annual Board notification",
    "Subject to formal peer review and written approval of the Board",
    "Within 30 calendar days of formal notice by certified mail",
    "Only in inpatient psychiatric facilities accredited by JCAHO",
    "Only under the direct supervision of a licensed psychologist",
    "Requires approval by a two-thirds majority of the Georgia Board",
    "Within 60 calendar days of the administrative determination",
    "Only after completing 20 additional hours of continuing education",
    "No, unless specifically authorized under a court order",
    "Yes, provided full written informed consent is documented in the record",
]


def normalize_text(text: str) -> str:
    """Normalize text by stripping trailing punctuation, whitespace, and lowercasing."""
    return re.sub(r"[\.;:!?,\\s]+$", "", text.strip().lower())


def parse_anki_tsv(tsv_path: Path | str | None = None) -> list[dict[str, Any]]:
    """Parse anki/gamb_deck.tsv into a list of card dictionaries.

    Skips comment lines starting with '#' and the header line 'front\\tback\\ttags'.
    Extracts front, back, source citation, cleaned answer text, and primary domain tag.
    """
    path = DEFAULT_TSV_PATH if tsv_path is None else Path(tsv_path)
    if not path.exists():
        raise FileNotFoundError(f"Anki deck TSV file not found: {path}")

    cards: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not lines:
        return cards

    # Check header
    first_line_parts = lines[0].split("\t")
    if first_line_parts[0].lower() == "front" and len(first_line_parts) >= 2:
        card_lines = lines[1:]
    else:
        card_lines = lines

    for index, line in enumerate(card_lines):
        parts = line.split("\t")
        if len(parts) < 2:
            continue

        front = parts[0].strip()
        back = parts[1].strip()
        tags_str = parts[2].strip() if len(parts) > 2 else ""
        tag_tokens = tags_str.split()

        # Primary domain: first token in tags matching one of the 6 official domains
        primary_domain = next(
            (t for t in tag_tokens if t in OFFICIAL_DOMAINS), "licensure"
        )
        subtopic = next((t for t in tag_tokens if t not in OFFICIAL_DOMAINS), None)

        # Extract citation and cleaned answer
        m = CITATION_REGEX.search(back)
        if m:
            citation = m.group(1).strip()
            raw_answer = back[: m.start()].strip()
        else:
            # Fallback citation based on domain/tags
            if "licensure" in tag_tokens or "rules-510-2" in tag_tokens:
                citation = "Rule 510-2-.01"
            elif "43-39" in tag_tokens:
                citation = "OCGA 43-39"
            else:
                citation = "Ga. Comp. R. & Regs. r. 510-1 et seq."
            raw_answer = back

        clean_answer = re.sub(r"[\.;:\s]+$", "", raw_answer).strip()

        cards.append(
            {
                "id": index,
                "front": front,
                "back": back,
                "answer_text": clean_answer,
                "source_citation": citation,
                "domain": primary_domain,
                "subtopic": subtopic,
                "raw_tags": tags_str,
            }
        )

    return cards


def generate_distractors(
    card: dict[str, Any],
    index: int,
    pool_by_domain: dict[str, list[dict[str, Any]]],
) -> list[str]:
    """Generate 3 distinct, plausible distractors for a card."""
    ans = card["answer_text"]
    norm_ans = normalize_text(ans)
    front = card["front"]
    domain = card["domain"]

    candidates: list[str] = []

    # 1. Numeric / Duration / Quantity substitution
    # Days pattern
    m_days = re.search(
        r"\b(\d+)\s+((?:calendar\s+|business\s+)?(?:days|day))\b",
        ans,
        re.IGNORECASE,
    )
    if m_days:
        val = int(m_days.group(1))
        unit = m_days.group(2)
        day_pool = [10, 14, 15, 30, 45, 60, 90, 120, 180, 365]
        alt_vals = sorted([d for d in day_pool if d != val], key=lambda d: abs(d - val))
        for alt in alt_vals[:4]:
            candidates.append(
                ans[: m_days.start()] + f"{alt} {unit}" + ans[m_days.end() :]
            )

    # Hours pattern
    m_hours = re.search(
        r"\b([\d,]+)\s+((?:clock\s+)?(?:hours|hour))\b",
        ans,
        re.IGNORECASE,
    )
    if m_hours and not candidates:
        raw_num = m_hours.group(1).replace(",", "")
        if raw_num.isdigit():
            val = int(raw_num)
            unit = m_hours.group(2)
            if val > 100:
                hour_pool = [500, 1000, 1500, 1750, 2000, 2500]
                alt_vals = sorted(
                    [h for h in hour_pool if h != val], key=lambda h: abs(h - val)
                )
                for alt in alt_vals[:4]:
                    candidates.append(
                        ans[: m_hours.start()]
                        + f"{alt:,} {unit}"
                        + ans[m_hours.end() :]
                    )
            else:
                hour_pool_short = [12, 24, 48, 72, 96]
                alt_vals = sorted(
                    [h for h in hour_pool_short if h != val],
                    key=lambda h: abs(h - val),
                )
                for alt in alt_vals[:4]:
                    candidates.append(
                        ans[: m_hours.start()]
                        + f"{alt} {unit}"
                        + ans[m_hours.end() :]
                    )

    # Years pattern
    m_years = re.search(
        r"\b(\d+|one|two|three|four|five|six|seven|ten)\s+(years|year)\b",
        ans,
        re.IGNORECASE,
    )
    if m_years and not candidates:
        word_to_num = {
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "ten": "10",
        }
        val_str = m_years.group(1).lower()
        val_norm = word_to_num.get(val_str, val_str)
        is_word = val_str in word_to_num
        unit = m_years.group(2)
        year_pool_words = ["Two", "Three", "Four", "Five", "Seven", "Ten"]
        year_pool_nums = ["1", "2", "3", "5", "7", "10"]
        if is_word:
            alt_vals_word = [y for y in year_pool_words if y.lower() != val_str]
            for alt in alt_vals_word[:4]:
                candidates.append(
                    ans[: m_years.start()] + f"{alt} {unit}" + ans[m_years.end() :]
                )
        else:
            alt_vals_num = [y for y in year_pool_nums if y != val_norm]
            for alt in alt_vals_num[:4]:
                candidates.append(
                    ans[: m_years.start()] + f"{alt} {unit}" + ans[m_years.end() :]
                )

    # Months pattern
    m_months = re.search(r"\b(\d+)\s+(months|month)\b", ans, re.IGNORECASE)
    if m_months and not candidates:
        val = int(m_months.group(1))
        unit = m_months.group(2)
        month_pool = [3, 6, 11, 12, 18, 24, 36]
        alt_vals = sorted([m for m in month_pool if m != val], key=lambda m: abs(m - val))
        for alt in alt_vals[:4]:
            candidates.append(
                ans[: m_months.start()] + f"{alt} {unit}" + ans[m_months.end() :]
            )

    # Members pattern
    m_members = re.search(
        r"\b(six|five|seven|eight|nine|three|four|\d+)\s+members?\b",
        ans,
        re.IGNORECASE,
    )
    if m_members and not candidates:
        candidates.extend(
            [
                "Five members: four licensed psychologists and one public/consumer member",
                "Seven members: six licensed psychologists and one public/consumer member",
                "Nine members: seven licensed psychologists and two public/consumer members",
            ]
        )

    # Dollars pattern
    m_dollars = re.search(r"\$([\d,]+)", ans)
    if m_dollars and not candidates:
        val_str = m_dollars.group(1).replace(",", "")
        dollar_pool = ["$250", "$500", "$1,000", "$2,500", "$5,000"]
        alt_vals_str = [d for d in dollar_pool if d.replace("$", "").replace(",", "") != val_str]
        for alt in alt_vals_str[:4]:
            candidates.append(
                ans[: m_dollars.start()] + alt + ans[m_dollars.end() :]
            )

    # 2. Entity / Role answers
    if norm_ans.startswith("the governor") or ans == "The Governor":
        candidates.extend(
            [
                "The Secretary of State",
                "The Attorney General",
                "The Georgia State Board of Examiners of Psychologists",
                "The Commissioner of Public Health",
            ]
        )
    elif "dfcs" in norm_ans or "child welfare" in norm_ans:
        candidates.extend(
            [
                "Georgia Composite Medical Board",
                "Department of Behavioral Health and Developmental Disabilities",
                "County Board of Health and Wellness",
                "Office of State Administrative Hearings",
            ]
        )
    elif "superior court" in norm_ans:
        candidates.extend(
            [
                "Office of State Administrative Hearings (OSAH)",
                "Georgia Court of Appeals",
                "Probate Court of the county of practice",
                "Federal District Court for the Northern District of Georgia",
            ]
        )
    elif norm_ans.startswith("eppp"):
        candidates.extend(
            [
                "The Georgia Board oral examination",
                "CPCCC (Comprehensive Psychology Competency Exam)",
                "ABPP Specialty Board Examination",
            ]
        )

    # 3. Yes / No answers
    is_yes = bool(re.match(r"^yes([;,\.\s]|$)", norm_ans))
    is_no = bool(re.match(r"^no([;,\.\s]|$)", norm_ans))
    if is_yes:
        candidates.extend(
            [
                "No; strictly prohibited under Georgia law and Board rules",
                "Only with prior written authorization from the Georgia State Board",
                "Only under an emergency judicial order or formal court subpoena",
            ]
        )
    elif is_no:
        candidates.extend(
            [
                "Yes, provided full written informed consent is documented in the client file",
                "Yes, at the independent clinical discretion of the licensed psychologist",
                "Yes, upon formal petition and written approval by the Board",
            ]
        )

    # 4. Domain pool matching
    same_dom_cards = pool_by_domain.get(domain, [])
    rng = random.Random(index * 37 + 11)
    shuffled_pool = list(same_dom_cards)
    rng.shuffle(shuffled_pool)

    # Sort by closeness in length to ans to keep distractors syntactically balanced
    shuffled_pool.sort(key=lambda c: abs(len(c["answer_text"]) - len(ans)))

    for c in shuffled_pool:
        c_ans = c["answer_text"]
        if normalize_text(c_ans) != norm_ans:
            candidates.append(c_ans)

    # Fallback to other domains
    for other_dom, clist in pool_by_domain.items():
        if other_dom != domain:
            for c in clist:
                candidates.append(c["answer_text"])

    # Append robust fallbacks
    candidates.extend(ROBUST_FALLBACKS)

    # Deduplicate and pick exactly 3
    final: list[str] = []
    seen: set[str] = {norm_ans}
    for cand in candidates:
        n_c = normalize_text(cand)
        if n_c and n_c not in seen:
            seen.add(n_c)
            final.append(cand)
            if len(final) == 3:
                break

    return final


def build_question_records(
    cards: list[dict[str, Any]] | None = None,
    tsv_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Build question records with 4 distinct options and uniform key distribution.

    Uniform key distribution assigns correct answer evenly across A, B, C, D
    (via card_index % 4).
    """
    if cards is None:
        cards = parse_anki_tsv(tsv_path=tsv_path)

    pool_by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for card in cards:
        pool_by_domain[card["domain"]].append(card)

    questions: list[dict[str, Any]] = []

    for index, card in enumerate(cards):
        distractors = generate_distractors(card, index, pool_by_domain)
        correct_answer = card["answer_text"]

        # Deterministically assign correct option to A (0), B (1), C (2), or D (3)
        correct_idx = index % 4
        correct_option_letter = chr(ord("A") + correct_idx)

        options: list[str] = ["", "", "", ""]
        options[correct_idx] = correct_answer

        distractor_idx = 0
        for slot in range(4):
            if slot != correct_idx:
                options[slot] = distractors[distractor_idx]
                distractor_idx += 1

        # Format explanation to include substantive answer and citation
        if f"({card['source_citation']})" in card["back"]:
            explanation = card["back"]
        else:
            explanation = f"{card['answer_text']}. ({card['source_citation']})"

        question_record = {
            "domain": card["domain"],
            "subtopic": card["subtopic"],
            "source_citation": card["source_citation"],
            "question_text": card["front"],
            "option_a": options[0],
            "option_b": options[1],
            "option_c": options[2],
            "option_d": options[3],
            "correct_option": correct_option_letter,
            "explanation": explanation,
            "answer_text": correct_answer,
        }
        questions.append(question_record)

    return questions


def seed_database(
    db_path: Path | str | None = None,
    tsv_path: Path | str | None = None,
) -> int:
    """Initialize database and seed all 435 question records.

    Returns the count of seeded questions.
    """
    target_db = DEFAULT_DB_PATH if db_path is None else Path(db_path)
    init_db(target_db)

    # Ensure idempotency: clear existing questions table
    conn = get_connection(target_db)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM session_answers")
            cursor.execute("DELETE FROM questions")
    finally:
        conn.close()

    questions = build_question_records(tsv_path=tsv_path)
    return insert_questions(questions, db_path=target_db)


if __name__ == "__main__":
    count = seed_database()
    print(f"Successfully seeded {count} questions into {DEFAULT_DB_PATH}.")
