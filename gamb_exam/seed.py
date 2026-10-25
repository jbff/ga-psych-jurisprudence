"""Question pool population and distractor generation engine.

Parses Georgia Jurisprudence Anki flashcards (anki/gamb_deck.tsv),
transforms cards into 4-choice multiple choice question records with
legally plausible distractors and code citations, and seeds data/gamb_exam.db.
"""

from __future__ import annotations

import json
import random
import re
import sqlite3
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
QUESTION_POOL_JSON = Path(__file__).parent / "question_pool.json"

CITATION_REGEX = re.compile(
    r"\(\s*((?:OCGA|Rule|O\.C\.G\.A\.|Board|APA|Code|Ga\.)[^)]*(?:\([^)]*\)[^)]*)*)\)\.?\s*$",
    re.IGNORECASE,
)

POLAR_QUESTION_STARTS = re.compile(
    r"^(can|may|is|are|does|do|must|should|could|would|shall)\b",
    re.IGNORECASE,
)

POLAR_NO_DISTRACTORS: list[str] = [
    "Yes, provided full written informed consent is documented in the client record",
    "Yes, upon formal written petition and prior approval by the Georgia State Board",
    "Yes, if authorized under an explicit court order or judicial subpoena",
    "Yes, at the independent clinical discretion of the licensed psychologist",
    "Yes, provided the arrangement is documented in writing and is not clinically contraindicated",
    "Yes, in emergency situations where failure to act poses imminent danger to life or safety",
    "Yes, if conducted under the direct supervision of a Board-approved licensed psychologist",
    "Yes, for temporary practice not exceeding 30 calendar days per calendar year",
    "Yes, provided all identifying client information is completely redacted or disguised",
    "Yes, after a mandatory waiting period of two years following service termination",
    "Yes, if approved by a majority vote of the Georgia State Board of Examiners",
    "Yes, under the physician-psychologist collaborative practice exception",
    "Yes, provided notice is given to the Secretary of State within 14 calendar days",
    "Yes, with advance written notification to the Board and client waiver of privilege",
]

POLAR_YES_DISTRACTORS: list[str] = [
    "No; strictly prohibited under Georgia statutory law and Board rules",
    "No, unless specifically authorized under an emergency judicial order",
    "Only with prior written authorization and credentialing from the Georgia State Board",
    "Only if the psychologist has completed a minimum of two years of postdoctoral experience",
    "Only in inpatient psychiatric facilities or hospitals accredited by JCAHO",
    "Only if full written disclosure is provided to and countersigned by the client in advance",
    "No, unless the Board waives the requirement upon formal written application",
    "Only when practicing under the direct supervision of a licensed physician or psychiatrist",
    "No; this constitutes an unwaivable conflict of interest under Board ethics rules",
    "Only during a declared state of public health emergency by the Governor",
    "No; requires prior formal peer review and clearance by the Board ethics committee",
    "Only for endorsement applicants with at least ten years of continuous active licensure",
    "No, unless approved by a two-thirds majority of the Georgia State Board",
    "Only after completing 20 additional hours of continuing education in professional ethics",
]

POLAR_ANSWER_PREFIX = re.compile(
    r"^(yes|no)([;,\.]|\s*$)",
    re.IGNORECASE,
)

NON_POLAR_FALLBACKS: list[str] = [
    "At the discretion of the psychologist with annual Board notification",
    "Subject to formal peer review and written approval of the Board",
    "Within 30 calendar days of formal notice by certified mail",
    "In inpatient psychiatric facilities accredited by JCAHO",
    "Under the direct supervision of a licensed psychologist",
    "Upon approval by a two-thirds majority of the Georgia Board",
    "Within 60 calendar days of the administrative determination",
    "Following completion of 20 additional hours of continuing education",
    "Administrative review and written clearance by the Division Director",
    "Formal documentation maintained in the permanent supervisory file",
]


def normalize_text(text: str) -> str:
    """Normalize text by stripping trailing punctuation, whitespace, and lowercasing."""
    return text.strip().rstrip(".;:!?,").strip().lower()


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

        # Card 425 fix: ensure fine reads "$500.00" even if source TSV has dropped digits
        if "not to exceed 00.00" in back:
            back = back.replace("not to exceed 00.00", "not to exceed $500.00")
        if "not to exceed 00.00" in raw_answer:
            raw_answer = raw_answer.replace("not to exceed 00.00", "not to exceed $500.00")

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

    # 1. Quantitative phrases: "No more than X", "No less than X", "Not less than X"
    m_no_more = re.search(
        r"\b(no\s+more\s+than|no\s+less\s+than|not\s+less\s+than)\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b",
        ans,
        re.IGNORECASE,
    )
    if m_no_more:
        num_tok = m_no_more.group(2)
        word_map = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
        }
        num_to_word = {
            1: "one",
            2: "two",
            3: "three",
            4: "four",
            5: "five",
            6: "six",
            7: "seven",
            8: "eight",
            9: "nine",
            10: "ten",
        }
        if num_tok.lower() in word_map:
            val = word_map[num_tok.lower()]
            alt_pool = [2, 3, 4, 5, 6, 7]
            alts = [num_to_word[n] for n in alt_pool if n != val]
            for alt in alts[:4]:
                candidates.append(
                    ans[: m_no_more.start(2)] + alt + ans[m_no_more.end(2) :]
                )
        elif num_tok.isdigit():
            val = int(num_tok)
            alt_pool_num = [1, 2, 3, 4, 5, 6]
            alts_num = [str(n) for n in alt_pool_num if n != val]
            for alt in alts_num[:4]:
                candidates.append(
                    ans[: m_no_more.start(2)] + alt + ans[m_no_more.end(2) :]
                )

    if "no less than once each month" in ans.lower():
        candidates.extend(
            [
                "No less than once each week",
                "No less than once every two weeks",
                "No less than once every 60 days",
            ]
        )

    # 2. Dollars pattern (with cents support for e.g. $500.00)
    m_dollars = re.search(r"\$([\d,]+(?:\.\d\d)?)", ans)
    if m_dollars and not candidates:
        val_str = m_dollars.group(1).replace(",", "")
        has_cents = "." in val_str
        float_val = float(val_str)
        dollar_pool = [250.0, 500.0, 1000.0, 2500.0, 5000.0]
        dollar_alts = [d for d in dollar_pool if abs(d - float_val) > 0.01]
        for alt in dollar_alts[:4]:
            formatted = f"${alt:,.2f}" if has_cents else f"${int(alt):,}"
            candidates.append(
                ans[: m_dollars.start()] + formatted + ans[m_dollars.end() :]
            )

    # 3. Numeric / Duration / Quantity substitution
    # Days pattern
    m_days = re.search(
        r"\b(\d+)\s+((?:calendar\s+|business\s+)?(?:days|day))\b",
        ans,
        re.IGNORECASE,
    )
    if m_days and not candidates:
        val = int(m_days.group(1))
        day_pool = [10, 14, 15, 30, 45, 60, 90, 120, 180, 365]
        alt_vals = sorted([d for d in day_pool if d != val], key=lambda d: abs(d - val))
        for alt in alt_vals[:4]:
            unit_str = "day" if alt == 1 else "days"
            candidates.append(
                ans[: m_days.start()] + f"{alt} {unit_str}" + ans[m_days.end() :]
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
            if val > 100:
                hour_pool = [500, 1000, 1500, 1750, 2000, 2500]
                alt_vals = sorted(
                    [h for h in hour_pool if h != val], key=lambda h: abs(h - val)
                )
                for alt in alt_vals[:4]:
                    unit_str = "hour" if alt == 1 else "hours"
                    candidates.append(
                        ans[: m_hours.start()]
                        + f"{alt:,} {unit_str}"
                        + ans[m_hours.end() :]
                    )
            else:
                hour_pool_short = [12, 24, 48, 72, 96]
                alt_vals = sorted(
                    [h for h in hour_pool_short if h != val],
                    key=lambda h: abs(h - val),
                )
                for alt in alt_vals[:4]:
                    unit_str = "hour" if alt == 1 else "hours"
                    candidates.append(
                        ans[: m_hours.start()]
                        + f"{alt} {unit_str}"
                        + ans[m_hours.end() :]
                    )

    # Years pattern with proper pluralization and capitalization
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
        is_start = m_years.start() == 0
        year_pool_words = ["one", "two", "three", "four", "five", "seven", "ten"]
        year_pool_nums = ["1", "2", "3", "5", "7", "10"]
        if is_word:
            alt_vals_word = [y for y in year_pool_words if y != val_str]
            for alt in alt_vals_word[:4]:
                unit_str = "year" if alt == "one" else "years"
                word_str = alt.capitalize() if is_start else alt.lower()
                candidates.append(
                    ans[: m_years.start()]
                    + f"{word_str} {unit_str}"
                    + ans[m_years.end() :]
                )
        else:
            alt_vals_num = [y for y in year_pool_nums if y != val_norm]
            for alt in alt_vals_num[:4]:
                unit_str = "year" if alt == "1" else "years"
                candidates.append(
                    ans[: m_years.start()]
                    + f"{alt} {unit_str}"
                    + ans[m_years.end() :]
                )

    # Months pattern
    m_months = re.search(r"\b(\d+)\s+(months|month)\b", ans, re.IGNORECASE)
    if m_months and not candidates:
        val = int(m_months.group(1))
        month_pool = [3, 6, 11, 12, 18, 24, 36]
        alt_vals = sorted([m for m in month_pool if m != val], key=lambda m: abs(m - val))
        for alt in alt_vals[:4]:
            unit_str = "month" if alt == 1 else "months"
            candidates.append(
                ans[: m_months.start()] + f"{alt} {unit_str}" + ans[m_months.end() :]
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

    # Percent pattern
    m_percent = re.search(r"\b(\d+)%\b", ans)
    if m_percent and not candidates:
        val = int(m_percent.group(1))
        pct_pool = [10, 20, 25, 50, 75, 80]
        pct_alts = [p for p in pct_pool if p != val]
        for alt in pct_alts[:4]:
            candidates.append(
                ans[: m_percent.start()] + f"{alt}%" + ans[m_percent.end() :]
            )

    # 4. Entity / Role answers
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

    # 5. Polar Yes/No handling
    # Apply polar Yes/No distractors ONLY IF:
    # - Question begins with polar auxiliary verb, OR
    # - Answer strictly starts with Yes/No followed by punctuation or end-of-string
    # (and not quantitative expressions like 'No more than', 'No less than', etc.)
    m_no_strictly = bool(
        re.match(r"^no([;,\.]|\s*$)", norm_ans)
    ) and not bool(re.match(r"^no\s+(more|less|later|earlier)\s+than\b", norm_ans))
    m_yes_strictly = bool(re.match(r"^yes([;,\.]|\s*$)", norm_ans))
    is_polar_q = bool(POLAR_QUESTION_STARTS.match(front))
    is_polar = (is_polar_q or m_no_strictly or m_yes_strictly) and (
        m_no_strictly or m_yes_strictly
    )

    rng = random.Random(index * 47 + 19)

    if is_polar and m_no_strictly:
        shuffled_no = list(POLAR_NO_DISTRACTORS)
        rng.shuffle(shuffled_no)
        candidates.extend(shuffled_no)
    elif is_polar and m_yes_strictly:
        shuffled_yes = list(POLAR_YES_DISTRACTORS)
        rng.shuffle(shuffled_yes)
        candidates.extend(shuffled_yes)

    # 6. Domain pool matching
    same_dom_cards = pool_by_domain.get(domain, [])
    shuffled_pool = list(same_dom_cards)
    rng.shuffle(shuffled_pool)

    # Sort by closeness in length to ans to keep distractors syntactically balanced
    shuffled_pool.sort(key=lambda c: abs(len(c["answer_text"]) - len(ans)))

    for c in shuffled_pool:
        c_ans = c["answer_text"]
        c_is_polar = bool(POLAR_ANSWER_PREFIX.match(c_ans.strip()))
        if not is_polar and c_is_polar:
            continue
        if is_polar and not c_is_polar:
            continue
        if normalize_text(c_ans) != norm_ans:
            candidates.append(c_ans)

    # Fallback to other domains
    for other_dom, clist in pool_by_domain.items():
        if other_dom != domain:
            for c in clist:
                c_ans = c["answer_text"]
                c_is_polar = bool(POLAR_ANSWER_PREFIX.match(c_ans.strip()))
                if not is_polar and c_is_polar:
                    continue
                if is_polar and not c_is_polar:
                    continue
                if normalize_text(c_ans) != norm_ans:
                    candidates.append(c_ans)

    # Append robust fallbacks
    if is_polar:
        if m_no_strictly:
            candidates.extend(POLAR_NO_DISTRACTORS)
        else:
            candidates.extend(POLAR_YES_DISTRACTORS)
    else:
        candidates.extend(NON_POLAR_FALLBACKS)

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

    Loads from question_pool.json when available, otherwise falls back to
    procedurally generating options from Anki deck cards.
    """
    if cards is None and tsv_path is None and QUESTION_POOL_JSON.exists():
        with open(QUESTION_POOL_JSON, "r", encoding="utf-8") as f:
            raw_pool = json.load(f)

        questions: list[dict[str, Any]] = []
        for q in raw_pool:
            correct_opt = q["correct_option"]
            ans_text = q["options"].get(correct_opt, "")
            questions.append(
                {
                    "id": q["id"],
                    "domain": q["domain"],
                    "subtopic": q.get("subtopic", "") or "",
                    "source_citation": q["source_citation"],
                    "question_text": q["question_text"],
                    "option_a": q["options"]["A"],
                    "option_b": q["options"]["B"],
                    "option_c": q["options"]["C"],
                    "option_d": q["options"]["D"],
                    "correct_option": correct_opt,
                    "explanation": q["explanation"],
                    "answer_text": ans_text,
                }
            )
        return questions

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
    """Initialize database and seed all 435 question records idempotently.

    Builds records before modifying the database.
    Resets the autoincrement primary key sequence so IDs start at 1.
    """
    target_db = DEFAULT_DB_PATH if db_path is None else Path(db_path)
    init_db(target_db)

    # 1. Build question records BEFORE modifying the database
    questions = build_question_records(tsv_path=tsv_path)

    # 2. Reset database tables and sqlite_sequence
    conn = get_connection(target_db)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM session_answers")
            cursor.execute("DELETE FROM questions")
            try:
                cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name IN ('questions', 'session_answers')"
                )
            except sqlite3.OperationalError:
                pass
    finally:
        conn.close()

    # 3. Insert fresh questions
    return insert_questions(questions, db_path=target_db)


if __name__ == "__main__":
    count = seed_database()
    print(f"Successfully seeded {count} questions into {DEFAULT_DB_PATH}.")
