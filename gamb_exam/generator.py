"""Stratified 50-question exam generator and markdown exporter for the Georgia Jurisprudence Exam."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

from gamb_exam.db import (
    ensure_db_initialized,
    get_connection,
)

DOMAIN_QUOTAS: dict[str, int] = {
    "prof-relationships": 14,
    "licensure": 13,
    "competence": 9,
    "assessment": 6,
    "privacy": 5,
    "recordkeeping": 3,
}

TOTAL_QUESTIONS: int = 50
PASSING_SCORE: int = 38
PASSING_PERCENT: float = 76.0

DOMAIN_DISPLAY_NAMES: dict[str, str] = {
    "prof-relationships": "Professional Relationships",
    "licensure": "Licensure and Regulations",
    "competence": "Competence",
    "assessment": "Assessment",
    "privacy": "Privacy and Confidentiality",
    "recordkeeping": "Recordkeeping and Fees",
}

LEGAL_DISCLAIMER: str = (
    "> [!WARNING]\n"
    "> **LEGAL & REGULATORY DISCLAIMER**:\n"
    "> The study materials, question pools, flashcards, reference sheets, and practice exams contained in this repository "
    "are **independently authored study aids** and are **NOT official examination materials** from the "
    "Georgia State Board of Examiners of Psychologists, PSI Services LLC, or the Association of State "
    "and Provincial Psychology Boards (ASPPB). While based on public statutory and regulatory texts "
    "(O.C.G.A. and Georgia Board Rules Chapter 510), these materials **have not been verified, reviewed, or approved "
    "by any licensing board, testing vendor, or regulatory authority**. Absolutely no claim, warranty, or representation "
    "is made that this content is official, correct, current, or complete, or that studying it will "
    "result in a passing score on the Georgia Jurisprudence Examination (GAMB). Laws and regulations change, "
    "and these materials may contain errors or omissions. Use of these materials is entirely at your own risk. "
    "The author and contributors disclaim all liability for any claims, damages, direct or consequential losses, "
    "examination outcomes, or reliance upon these materials."
)

LEGAL_DISCLAIMER_HTML: str = (
    "The study materials, question pools, flashcards, reference sheets, and practice exams contained in this repository "
    "are <strong>independently authored study aids</strong> and are <strong>NOT official examination materials</strong> "
    "from the Georgia State Board of Examiners of Psychologists, PSI Services LLC, or the Association of State "
    "and Provincial Psychology Boards (ASPPB). While based on public Georgia statutes (O.C.G.A.) and Board Rules "
    "(Chapter 510), these materials <strong>have not been verified, reviewed, or approved by any licensing board, "
    "testing vendor, or regulatory authority</strong>. Absolutely no claim, warranty, or representation is made "
    "that this content is official, correct, current, or complete, or that using it will result in a passing score "
    "on the Georgia Jurisprudence Examination (GAMB). Laws and regulations change, and these materials may contain "
    "errors or omissions. Use of these materials is entirely at your own risk. The author and contributors disclaim "
    "all liability for any claims, damages, direct or consequential losses, examination outcomes, or reliance upon these materials."
)


def shuffle_question_options(
    question: dict[str, Any], rng: random.Random | None = None
) -> dict[str, Any]:
    """Dynamically shuffle options A, B, C, D for a question and update correct_option."""
    q = dict(question)
    _rng = rng if rng is not None else random.Random()

    orig_correct_letter = q["correct_option"].strip().upper()
    orig_options = {
        "A": q["option_a"],
        "B": q["option_b"],
        "C": q["option_c"],
        "D": q["option_d"],
    }

    pairs = [
        (orig_options["A"], orig_correct_letter == "A"),
        (orig_options["B"], orig_correct_letter == "B"),
        (orig_options["C"], orig_correct_letter == "C"),
        (orig_options["D"], orig_correct_letter == "D"),
    ]
    _rng.shuffle(pairs)

    letters = ["A", "B", "C", "D"]
    for idx, (text, is_correct) in enumerate(pairs):
        letter = letters[idx]
        q[f"option_{letter.lower()}"] = text
        if is_correct:
            q["correct_option"] = letter

    return q


def generate_exam_questions(
    db_path: Path | str | None = None,
    prioritize_unseen: bool = True,
    shuffle_options: bool = True,
    rng: random.Random | None = None,
) -> list[dict[str, Any]]:
    """Generate a stratified 50-question exam matching official Board domain quotas.

    Args:
        db_path: Path to the SQLite database. If None, uses DEFAULT_DB_PATH.
        prioritize_unseen: If True, prioritizes questions answered least often in prior sessions.
        shuffle_options: If True, shuffles options A, B, C, D dynamically.
        rng: Optional Random instance for deterministic generation.

    Returns:
        List of 50 sampled question dicts.
    """
    ensure_db_initialized(db_path)
    _rng = rng if rng is not None else random.Random()
    conn = get_connection(db_path)
    if rng is not None:
        conn.create_function(
            "RANDOM",
            0,
            lambda: rng.randint(-9223372036854775808, 9223372036854775807),
        )

    sampled_questions: list[dict[str, Any]] = []

    try:
        cursor = conn.cursor()
        for domain, quota in DOMAIN_QUOTAS.items():
            if prioritize_unseen:
                query = """
                    SELECT q.*, COUNT(sa.id) AS times_answered
                    FROM questions q
                    LEFT JOIN session_answers sa ON q.id = sa.question_id
                    WHERE q.domain = ?
                    GROUP BY q.id
                    ORDER BY times_answered ASC, RANDOM()
                    LIMIT ?
                """
            else:
                query = """
                    SELECT q.*
                    FROM questions q
                    WHERE q.domain = ?
                    ORDER BY RANDOM()
                    LIMIT ?
                """
            cursor.execute(query, (domain, quota))
            rows = cursor.fetchall()
            if len(rows) < quota:
                raise ValueError(
                    f"Insufficient questions in domain '{domain}': requested {quota}, found {len(rows)}"
                )
            for row in rows:
                sampled_questions.append(dict(row))
    finally:
        conn.close()

    # Shuffle the combined 50 questions across domains
    _rng.shuffle(sampled_questions)

    # Optionally shuffle options A, B, C, D for each question
    if shuffle_options:
        sampled_questions = [
            shuffle_question_options(q, rng=_rng) for q in sampled_questions
        ]

    return sampled_questions


def export_mock_markdown(
    questions: list[dict[str, Any]],
    output_dir: Path | str = "mocks",
    mock_id: int | str | None = None,
) -> tuple[Path, Path]:
    """Export questions and answer key to Markdown files.

    Args:
        questions: List of 50 question dicts.
        output_dir: Target directory for exported files.
        mock_id: Optional identifier for filenames and titles.

    Returns:
        Tuple of (questions_path, key_path).
    """
    if len(questions) != TOTAL_QUESTIONS:
        raise ValueError(
            f"Expected {TOTAL_QUESTIONS} questions, got {len(questions)}"
        )

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    if mock_id is None:
        q_filename = "mock_questions.md"
        k_filename = "mock_key.md"
        exam_title = "Mock Exam"
    elif isinstance(mock_id, int):
        q_filename = f"mock{mock_id}_questions.md"
        k_filename = f"mock{mock_id}_key.md"
        exam_title = f"Mock Exam #{mock_id}"
    else:
        str_id = str(mock_id)
        if str_id.startswith("mock"):
            q_filename = f"{str_id}_questions.md"
            k_filename = f"{str_id}_key.md"
            exam_title = f"Mock Exam ({str_id})"
        else:
            q_filename = f"mock_{str_id}_questions.md"
            k_filename = f"mock_{str_id}_key.md"
            exam_title = f"Mock Exam ({str_id})"

    questions_path = out_path / q_filename
    key_path = out_path / k_filename

    # Build questions content
    q_lines = [
        f"# Georgia Psychology Jurisprudence Examination — {exam_title}",
        "",
        LEGAL_DISCLAIMER,
        "",
        "## Exam Instructions",
        "- **Time limit:** 60 minutes",
        f"- **Number of questions:** {TOTAL_QUESTIONS} multiple-choice questions",
        f"- **Passing score:** {PASSING_SCORE} out of {TOTAL_QUESTIONS} ({PASSING_PERCENT:.1f}%)",
        "- **Format:** Closed book, 4 options per question (A, B, C, D).",
        "- Select the single best answer for each question.",
        "",
        "---",
        "",
    ]

    for idx, q in enumerate(questions, start=1):
        q_lines.extend(
            [
                f"**Q{idx}.** {q['question_text']}",
                "",
                f"A. {q['option_a']}",
                f"B. {q['option_b']}",
                f"C. {q['option_c']}",
                f"D. {q['option_d']}",
                "",
                "---",
                "",
            ]
        )

    # Build key content
    k_lines = [
        f"# Georgia Psychology Jurisprudence Examination — {exam_title} Answer Key",
        "",
        LEGAL_DISCLAIMER,
        "",
        "## Domain Score Worksheet",
        "",
        "Use this worksheet to calculate your domain scores and diagnose areas needing further review.",
        "",
        "| Domain | Total Items | Your Score | Target % (>=70%) | Status |",
        "|:-------|:-----------:|:----------:|:----------------:|:------:|",
    ]

    for domain_code, quota in DOMAIN_QUOTAS.items():
        disp_name = DOMAIN_DISPLAY_NAMES.get(domain_code, domain_code)
        target_correct = round(quota * 0.70)
        k_lines.append(
            f"| {disp_name} (`{domain_code}`) | {quota} | / {quota} | {target_correct}/{quota} (70%) | [ ] Pass  [ ] Review |"
        )

    k_lines.extend(
        [
            f"| **Total Exam** | **{TOTAL_QUESTIONS}** | **/ {TOTAL_QUESTIONS}** | **Passing: {PASSING_SCORE}/{TOTAL_QUESTIONS} ({PASSING_PERCENT:.1f}%)** | [ ] PASS  [ ] FAIL |",
            "",
            "### Scoring Guide",
            f"- **{PASSING_SCORE}–{TOTAL_QUESTIONS} correct:** Passing score. You meet the minimum Georgia Jurisprudence standard.",
            f"- **Below {PASSING_SCORE}:** Not passing. Review missed domains and re-take after focused study.",
            "- **Domain-level target:** Aim for at least 70% in each domain to ensure balanced preparation.",
            "",
            "---",
            "",
            "## Answer Key & Explanations",
            "",
            "| Q# | Domain | Answer | Citation | Explanation |",
            "|:--:|:-------|:------:|:---------|:------------|",
        ]
    )

    for idx, q in enumerate(questions, start=1):
        clean_citation = str(q.get("source_citation", "")).replace("|", "\\|").replace("\n", " ").strip()
        clean_explanation = str(q.get("explanation", "")).replace("|", "\\|").replace("\n", " ").strip()
        k_lines.append(
            f"| {idx} | {q.get('domain', '')} | {q.get('correct_option', '')} | {clean_citation} | {clean_explanation} |"
        )

    k_lines.extend(
        [
            "",
            "---",
            "",
            "## Detailed Item-by-Item Review",
            "",
        ]
    )

    for idx, q in enumerate(questions, start=1):
        k_lines.extend(
            [
                f"### Question {idx}",
                f"- **Domain:** `{q.get('domain', '')}`",
                f"- **Question:** {q.get('question_text', '')}",
                f"- **Correct Answer:** {q.get('correct_option', '')}",
                f"- **Citation:** {q.get('source_citation', '')}",
                f"- **Explanation:** {q.get('explanation', '')}",
                "",
            ]
        )

    questions_path.write_text("\n".join(q_lines), encoding="utf-8")
    key_path.write_text("\n".join(k_lines), encoding="utf-8")

    return (questions_path, key_path)
