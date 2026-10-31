# Per-Item Study Progress (`progress`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `gamb-exam progress` subcommand reporting cumulative per-item study statistics by domain, with an optional `--missed` list of questions last answered wrong.

**Architecture:** Two additive SQLite query functions in `db.py` feed one new Rich-rendering CLI handler in `cli.py`. No schema changes, no changes to existing queries or commands.

**Tech Stack:** Python ≥ 3.10, SQLite3, Rich, pytest.

**Spec:** `docs/superpowers/specs/2026-10-31-item-progress-stats-design.md`

## Global Constraints

- Every statistic excludes rows with `selected_option IS NULL`; the TUI persists skips as `is_correct = 0`.
- A question is **seen** if it has ≥1 answered row; **ever wrong** if it has ≥1 answered row with `is_correct = 0`; **clean** = seen − ever wrong.
- Both `timed_exam` and `study_drill` session rows count; there is no mode filter.
- All six canonical domains (`DOMAIN_QUOTAS` keys) must appear even when unseen; unknown DB domains appear after them.
- Empty or partially seeded databases must print zeros and exit `0`.
- Do not modify `get_missed_questions`, `get_study_questions`, `stats`, `missed`, or `study` behavior.
- Use the repository's existing Rich `Console`/`Table` conventions in `cli.py`.

## Review Focus

1. **TUI-saved skips** (`selected_option IS NULL`, `is_correct = 0`) must never count as seen or wrong, nor appear in `--missed`. Covered by Task 1 (`q3`, `q6`), Task 2 (`q2`, `q3`, `q5`), and Task 3's missed-list test.
2. **Wrong once, right later**: stays "ever wrong" in the category table but must drop out of the currently-missed list. Covered by Task 1 (`q2`) and Task 2 (`q1`).
3. **Right, then later skipped**: the skip must not make the item appear as missed. Covered by Task 2 (`q5`).
4. **Empty history or partially seeded DB**: zeroed learned counts, no division by zero, exit `0`. Covered by Task 3's empty/partial tests (the empty DB is auto-seeded to the 435-question pool by `ensure_db_initialized`).
5. **Unknown domain slug in the DB**: rendered after the canonical six without `KeyError`. Covered by Task 3's unknown-domain test.

---

### Task 1: `get_study_progress` query

**Files:**
- Modify: `gamb_exam/db.py` (append after `get_study_questions`)
- Test: `tests/test_db.py`

**Interfaces:**
- Consumes: existing `questions` and `session_answers` tables.
- Produces: `get_study_progress(db_path: Path | str | None = None) -> list[dict[str, Any]]`, where each dict has keys `domain`, `total_items`, `seen_items`, `clean_items`, `ever_wrong_items` (all `int` except `domain: str`). `clean_items` is computed in Python as `seen_items - ever_wrong_items`.

- [ ] **Step 1: Write the failing test**

Add the import `get_study_progress` to the `from gamb_exam.db import (...)` block in `tests/test_db.py`, then append:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_db.py::test_get_study_progress -v`
Expected: FAIL with `ImportError: cannot import name 'get_study_progress'`.

- [ ] **Step 3: Implement `get_study_progress`**

Append to `gamb_exam/db.py`:

```python
def get_study_progress(db_path: Path | str | None = None) -> list[dict[str, Any]]:
    """Return per-domain counts of seen, clean, and ever-wrong questions.

    Skipped answers (selected_option IS NULL) are ignored entirely.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT q.domain,
                   COUNT(DISTINCT q.id) AS total_items,
                   COUNT(DISTINCT CASE WHEN sa.selected_option IS NOT NULL
                                       THEN q.id END) AS seen_items,
                   COUNT(DISTINCT CASE WHEN sa.selected_option IS NOT NULL
                                        AND sa.is_correct = 0
                                       THEN q.id END) AS ever_wrong_items
            FROM questions q
            LEFT JOIN session_answers sa ON sa.question_id = q.id
            GROUP BY q.domain
            ORDER BY q.domain
            """
        )
        rows = []
        for row in cursor.fetchall():
            seen = row["seen_items"]
            wrong = row["ever_wrong_items"]
            rows.append(
                {
                    "domain": row["domain"],
                    "total_items": row["total_items"],
                    "seen_items": seen,
                    "clean_items": seen - wrong,
                    "ever_wrong_items": wrong,
                }
            )
        return rows
    finally:
        conn.close()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_db.py::test_get_study_progress -v`
Expected: PASS.

- [ ] **Step 5: Run the database test file**

Run: `uv run pytest tests/test_db.py -v`
Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add gamb_exam/db.py tests/test_db.py
git commit -m "$(cat <<'EOF'
feat(db): add get_study_progress per-domain item aggregates

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: `get_last_wrong_questions` query

**Files:**
- Modify: `gamb_exam/db.py` (append after `get_study_progress`)
- Test: `tests/test_db.py`

**Interfaces:**
- Consumes: existing `questions` and `session_answers` tables.
- Produces: `get_last_wrong_questions(db_path: Path | str | None = None) -> list[dict[str, Any]]`, returning full question rows (`dict` with `id`, `domain`, `question_text`, `source_citation`, etc.) ordered by `domain ASC, id ASC`.

- [ ] **Step 1: Write the failing test**

Add the import `get_last_wrong_questions` to the `from gamb_exam.db import (...)` block in `tests/test_db.py`, then append:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_db.py::test_get_last_wrong_questions -v`
Expected: FAIL with `ImportError: cannot import name 'get_last_wrong_questions'`.

- [ ] **Step 3: Implement `get_last_wrong_questions`**

Append to `gamb_exam/db.py`:

```python
def get_last_wrong_questions(db_path: Path | str | None = None) -> list[dict[str, Any]]:
    """Return questions whose most recent answered attempt was incorrect.

    Unlike get_missed_questions, skipped rows are excluded before ranking so a
    later skip cannot mask or replace an earlier wrong answer.
    """
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT q.*
            FROM questions q
            JOIN (
                SELECT question_id, is_correct,
                       ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY id DESC) AS rn
                FROM session_answers
                WHERE selected_option IS NOT NULL
            ) latest ON q.id = latest.question_id AND latest.rn = 1
            WHERE latest.is_correct = 0
            ORDER BY q.domain ASC, q.id ASC
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_db.py::test_get_last_wrong_questions -v`
Expected: PASS.

- [ ] **Step 5: Run the database test file**

Run: `uv run pytest tests/test_db.py -v`
Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add gamb_exam/db.py tests/test_db.py
git commit -m "$(cat <<'EOF'
feat(db): add get_last_wrong_questions for currently missed items

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: `progress` subcommand, README, and CLI tests

**Files:**
- Modify: `gamb_exam/cli.py` (imports, `_truncate`, `handle_progress`, parser entry)
- Modify: `README.md` (quickstart block around line 128 and subcommand reference around line 195)
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `get_study_progress`, `get_last_wrong_questions` from Task 1–2; `DOMAIN_QUOTAS` and `DOMAIN_DISPLAY_NAMES` from `gamb_exam.generator`.
- Produces: `handle_progress(args: argparse.Namespace) -> int`, wired to `args.func`; `_truncate(text: str, limit: int = 80) -> str`; the subcommand `progress [--db PATH] [--missed]`.

- [ ] **Step 1: Write the failing CLI tests**

Append to `tests/test_cli.py`:

```python
def test_cli_progress_command_empty(tmp_db_path: Path, capsys: pytest.CaptureFixture[str]):
    """Progress with no answers prints zeroed stats and exits 0.

    handle_progress calls ensure_db_initialized, so an empty DB is auto-seeded
    with the 435-question pool; the learned counts still start at zero.
    """
    from gamb_exam.cli import main

    init_db(tmp_db_path)

    ret = main(["progress", "--db", str(tmp_db_path)])
    assert ret == 0
    out = capsys.readouterr().out
    assert "Items studied: 0 / 435 (0.0%)" in out
    assert "Clean: 0 (0.0%)" in out
    assert "Ever wrong: 0 (0.0%)" in out
    assert "Competence" in out


def test_cli_progress_command(tmp_db_path: Path, capsys: pytest.CaptureFixture[str]):
    """Progress reports seen/clean/ever-wrong counts and percentages."""
    from gamb_exam.cli import main

    init_db(tmp_db_path)
    q1 = insert_question(
        {
            "domain": "competence",
            "subtopic": "ethics",
            "source_citation": "O.C.G.A. § 43-39-1",
            "question_text": "Competence question?",
            "option_a": "A",
            "option_b": "B",
            "option_c": "C",
            "option_d": "D",
            "correct_option": "A",
            "explanation": "Because.",
        },
        db_path=tmp_db_path,
    )
    q2 = insert_question(
        {
            "domain": "assessment",
            "subtopic": "testing",
            "source_citation": "O.C.G.A. § 43-39-2",
            "question_text": "Assessment question?",
            "option_a": "A",
            "option_b": "B",
            "option_c": "C",
            "option_d": "D",
            "correct_option": "A",
            "explanation": "Because.",
        },
        db_path=tmp_db_path,
    )
    s1 = create_session(mode="study_drill", total_questions=2, db_path=tmp_db_path)
    save_session_answer(s1, q1, "B", is_correct=False, db_path=tmp_db_path)
    save_session_answer(s1, q2, "A", is_correct=True, db_path=tmp_db_path)

    ret = main(["progress", "--db", str(tmp_db_path)])
    assert ret == 0
    out = capsys.readouterr().out
    assert "Items studied: 2 / 2 (100.0%)" in out
    assert "Clean: 1 (50.0%)" in out
    assert "Ever wrong: 1 (50.0%)" in out
    assert "Competence" in out
    assert "Assessment" in out


def test_cli_progress_missed_list(tmp_db_path: Path, capsys: pytest.CaptureFixture[str]):
    """--missed lists last-answered-wrong questions and clears when graduated."""
    from gamb_exam.cli import main

    init_db(tmp_db_path)
    q1 = insert_question(
        {
            "domain": "competence",
            "subtopic": "ethics",
            "source_citation": "O.C.G.A. § 43-39-1",
            "question_text": "Dual relationship rule?",
            "option_a": "A",
            "option_b": "B",
            "option_c": "C",
            "option_d": "D",
            "correct_option": "A",
            "explanation": "Because.",
        },
        db_path=tmp_db_path,
    )
    s1 = create_session(mode="study_drill", total_questions=1, db_path=tmp_db_path)
    save_session_answer(s1, q1, "B", is_correct=False, db_path=tmp_db_path)

    ret = main(["progress", "--db", str(tmp_db_path), "--missed"])
    assert ret == 0
    out = capsys.readouterr().out
    assert "Currently Missed" in out
    assert "Dual" in out

    s2 = create_session(mode="study_drill", total_questions=1, db_path=tmp_db_path)
    save_session_answer(s2, q1, "A", is_correct=True, db_path=tmp_db_path)

    ret = main(["progress", "--db", str(tmp_db_path), "--missed"])
    assert ret == 0
    out = capsys.readouterr().out
    assert "No questions currently missed." in out


def test_cli_progress_unknown_domain(tmp_db_path: Path, capsys: pytest.CaptureFixture[str]):
    """An unrecognized domain slug is shown after the canonical six without error."""
    from gamb_exam.cli import main

    init_db(tmp_db_path)
    insert_question(
        {
            "domain": "new-domain",
            "subtopic": "misc",
            "source_citation": "O.C.G.A. § 43-39-9",
            "question_text": "New domain question?",
            "option_a": "A",
            "option_b": "B",
            "option_c": "C",
            "option_d": "D",
            "correct_option": "A",
            "explanation": "Because.",
        },
        db_path=tmp_db_path,
    )

    ret = main(["progress", "--db", str(tmp_db_path)])
    assert ret == 0
    out = capsys.readouterr().out
    assert "new-domain" in out
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli.py -k progress -v`
Expected: FAIL — `progress` is an invalid choice, so `main` returns `2` instead of `0`.

- [ ] **Step 3: Implement the subcommand**

In `gamb_exam/cli.py`:

1. Extend the `from gamb_exam.db import (...)` block with `get_last_wrong_questions` and `get_study_progress`.
2. Extend the `from gamb_exam.generator import (...)` block with `DOMAIN_DISPLAY_NAMES` and `DOMAIN_QUOTAS`.
3. Add these helpers after `handle_stats`:

```python
def _truncate(text: str, limit: int = 80) -> str:
    """Collapse whitespace and truncate to limit characters with an ellipsis."""
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def handle_progress(args: argparse.Namespace) -> int:
    """Handle the 'progress' subcommand to display cumulative per-item study stats."""
    ensure_db_initialized(args.db)
    rows = get_study_progress(db_path=args.db)
    by_domain = {row["domain"]: row for row in rows}

    ordered_domains = list(DOMAIN_QUOTAS.keys())
    ordered_domains += sorted(d for d in by_domain if d not in DOMAIN_QUOTAS)

    data = []
    for domain in ordered_domains:
        row = by_domain.get(domain)
        if row is None:
            total = seen = clean = wrong = 0
        else:
            total = row["total_items"]
            seen = row["seen_items"]
            clean = row["clean_items"]
            wrong = row["ever_wrong_items"]
        data.append((domain, total, seen, clean, wrong))

    total_items = sum(item[1] for item in data)
    seen_total = sum(item[2] for item in data)
    clean_total = sum(item[3] for item in data)
    wrong_total = sum(item[4] for item in data)

    coverage_total = f"{seen_total / total_items * 100:.1f}%" if total_items else "0.0%"
    clean_pct = f"{clean_total / seen_total * 100:.1f}%" if seen_total else "0.0%"
    wrong_pct = f"{wrong_total / seen_total * 100:.1f}%" if seen_total else "0.0%"
    console.print(
        f"[bold]Items studied:[/bold] {seen_total} / {total_items} ({coverage_total}) | "
        f"[bold]Clean:[/bold] {clean_total} ({clean_pct}) | "
        f"[bold]Ever wrong:[/bold] {wrong_total} ({wrong_pct})"
    )
    console.print()

    table = Table(title="Study Progress by Domain")
    table.add_column("Category", style="bold")
    table.add_column("Seen / Total", justify="right", no_wrap=True)
    table.add_column("Coverage", justify="right", no_wrap=True)
    table.add_column("Clean", justify="right", no_wrap=True)
    table.add_column("Ever Wrong", justify="right", no_wrap=True)
    table.add_column("% Ever Wrong", justify="right", no_wrap=True)

    for domain, total, seen, clean, wrong in data:
        coverage = f"{seen / total * 100:.1f}%" if total else "—"
        pct_wrong = f"{wrong / seen * 100:.1f}%" if seen else "—"
        table.add_row(
            DOMAIN_DISPLAY_NAMES.get(domain, domain),
            f"{seen} / {total}",
            coverage,
            str(clean),
            str(wrong),
            pct_wrong,
        )

    console.print(table)

    if args.missed:
        console.print()
        missed = get_last_wrong_questions(db_path=args.db)
        if not missed:
            console.print("[dim]No questions currently missed.[/dim]")
            return 0
        missed_table = Table(title="Currently Missed Questions (last answered wrong)")
        missed_table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        missed_table.add_column("Category", no_wrap=True)
        missed_table.add_column("Question")
        missed_table.add_column("Citation", style="dim")
        for q in missed:
            missed_table.add_row(
                str(q["id"]),
                DOMAIN_DISPLAY_NAMES.get(q["domain"], q["domain"]),
                _truncate(q["question_text"]),
                q["source_citation"],
            )
        console.print(missed_table)

    return 0
```

4. Register the parser between the `missed` and `stats` parsers in `create_parser`:

```python
    progress_parser = subparsers.add_parser(
        "progress",
        help="View cumulative per-item study progress broken down by domain",
    )
    progress_parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database file (default: {DEFAULT_DB_PATH})",
    )
    progress_parser.add_argument(
        "--missed",
        action="store_true",
        default=False,
        help="Also list questions whose most recent answered attempt was wrong",
    )
    progress_parser.set_defaults(func=handle_progress)
```

- [ ] **Step 4: Run the CLI tests to verify they pass**

Run: `uv run pytest tests/test_cli.py -k progress -v`
Expected: 4 tests PASS.

- [ ] **Step 5: Update `README.md`**

Add to the quickstart block after the `stats` example:

```bash
# View cumulative per-item study progress by domain
uv run gamb-exam progress --missed
```

Add to the "Complete CLI Subcommands Reference" list after the `stats` bullet:

```markdown
- **`uv run gamb-exam progress [--missed]`**  
  Cumulative per-item study statistics across all practice sessions. Shows how many distinct questions you have seen in each domain, how many you have never answered wrong ("clean"), and how many you have ever answered wrong. The `--missed` flag also lists questions whose most recent answered attempt was wrong.
```

- [ ] **Step 6: Run the full test suite**

Run: `uv run pytest -q`
Expected: all tests PASS, no failures.

- [ ] **Step 7: Commit**

```bash
git add gamb_exam/cli.py tests/test_cli.py README.md
git commit -m "$(cat <<'EOF'
feat(cli): add progress subcommand for per-item study stats

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
)"
```
