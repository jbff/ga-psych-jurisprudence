# Design Specification: `progress` — Per-Item Study Statistics by Category

**Date:** 2026-10-31
**Status:** Proposed (awaiting approval)
**Scope:** CLI (`gamb_exam/db.py`, `gamb_exam/cli.py`), tests, README

---

## 1. Intent and Why

`gamb-exam stats` reports one row per exam session. The learner also wants a
cumulative, per-item view across all recorded answers: how many distinct items
they have seen, how those items split across the six domains, and how many
items in each domain they got right without needing restudy.

The learner's mental model:

- **Category report** answers "how much of this domain did I get right cold?"
  → count items **ever answered wrong**, and its complement, items **never
  wrong** (clean).
- **The list** answers "what should I restudy now?" → questions whose **most
  recent** answer was wrong.

These are different questions, and both are wanted.

## 2. Goals, Non-Goals, Anti-Goals

**Goals**

- New `gamb-exam progress` subcommand.
- Overall and per-domain counts: items seen, clean (never wrong), ever wrong.
- Optional `--missed` flag that appends the currently-missed question list.
- Exclude skipped questions (`selected_option IS NULL`) everywhere: the TUI
  persists the whole drill on submit, so skips would otherwise be counted as
  seen-and-wrong.

**Non-Goals**

- No schema change; all data already exists in `session_answers` and `questions`.
- No web quizzer changes (its stats modal already covers this ground).
- No changes to the existing `stats`, `missed`, or `study` behavior.
- No first-attempt / last-attempt history charts.

**Anti-Goals**

- Adding another metric definition that makes the categories hard to read.
- Showing an item as "wrong" when the learner merely skipped it.

## 3. Constraints

- Python ≥ 3.10, SQLite (window functions already used in `get_missed_questions`).
- Output uses the existing `rich` console/table conventions in `cli.py`.
- Both `test` and `study` sessions count; there is no mode filter.
- The CLI must remain usable with zero history and with a partially seeded DB.

## 4. Approaches Considered

| Option | Description | Trade-off |
| :--- | :--- | :--- |
| **A (chosen)** | New `progress` subcommand; default shows overall + per-domain table; `--missed` appends the last-wrong list. | One command and one mental model; slightly larger single command. |
| B | `progress` for the table, add `--list` to the existing `missed` drill. | Cleaner separation, but touches existing command and splits the report. |
| C | Add `--by-category` to `stats`. | Fewer commands, but muddies `stats`' per-exam purpose. |

The learner picked **A**.

## 5. Definitions

- **Answered row**: `session_answers` row with `selected_option IS NOT NULL`.
- **Seen item**: a question with at least one answered row, across all sessions.
- **Clean item**: a seen item with no answered row where `is_correct = 0`.
- **Ever-wrong item**: a seen item with at least one answered row where
  `is_correct = 0`.
- Therefore `clean + ever_wrong = seen`.
- **Currently missed**: a question whose most recent *answered* row is
  incorrect. Skipped rows are ignored when determining "most recent answered".

## 6. Data Layer (`gamb_exam/db.py`)

### `get_study_progress(db_path=None) -> list[dict[str, Any]]`

Returns one row per domain present in `questions`:

| Key | Meaning |
| :--- | :--- |
| `domain` | domain slug |
| `total_items` | questions in the domain |
| `seen_items` | distinct questions with ≥1 answered row |
| `clean_items` | seen questions with zero wrong answered rows |
| `ever_wrong_items` | seen questions with ≥1 wrong answered row |

```sql
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
```

`clean_items` is derived in Python as `seen_items - ever_wrong_items`.

### `get_last_wrong_questions(db_path=None) -> list[dict[str, Any]]`

Returns full question rows whose latest **answered** attempt was incorrect,
ordered by domain then id. Unlike `get_missed_questions`, skipped rows are
filtered out *before* the window function so a later skip cannot mask or
replace a previous wrong answer.

```sql
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
```

`get_missed_questions` is left unchanged to avoid altering the `missed` drill.

## 7. CLI (`gamb_exam/cli.py`)

### Parser

```text
gamb-exam progress [--db PATH] [--missed]
```

- `--db`: same default and help as the other subcommands.
- `--missed`: also print the currently-missed questions.

### `handle_progress`

1. `ensure_db_initialized(args.db)`.
2. Load progress rows; merge against the six canonical domains from
   `generator.DOMAIN_QUOTAS` (and `DOMAIN_DISPLAY_NAMES`), appending any
   unknown domains found in the DB. Unseen canonical domains show zeros.
3. Print a summary line:
   `Items studied: X / N (Y%) | Clean: A (B%) | Ever wrong: C (D%)`
4. Print the per-domain table:

   | Column | Content |
   | :--- | :--- |
   | Category | display name |
   | Seen / Total | `seen / total` |
   | Coverage | `seen / total * 100`, `—` when total is 0 |
   | Clean | `clean_items` |
   | Ever Wrong | `ever_wrong_items` |
   | % Ever Wrong | `ever_wrong / seen * 100`, `—` when seen is 0 |

5. If `--missed`, print a second table: ID, Category (display name),
   Question (stem truncated to ~80 characters), Citation. If the list is
   empty, print a dim "No questions currently missed." line.
6. Return `0` in all non-error cases, including zero history.

### README

Add `progress` to the quickstart block and the "Complete CLI Subcommands
Reference" section.

## 8. Error Handling

- Zero questions / zero answers: zeroed table and summary, exit 0.
- Unknown domains in the DB: included after the canonical six.
- DB unreadable/seeding failure: existing `ensure_db_initialized` behavior.

## 9. Testing Plan

1. `tests/test_db.py`
   - `get_study_progress`: multiple domains; answered and skipped rows;
     repeated attempts; item wrong once then right stays ever-wrong; clean
     count correct; unseen questions not counted as seen.
   - `get_last_wrong_questions`: latest answered wrong included; latest
     answered correct excluded; skipped-only item excluded; a skip after a
     wrong answer does not remove or change it.
2. `tests/test_cli.py`
   - `progress` with empty DB: exit 0, zeros/summary present.
   - `progress` with populated answers: expected counts and percentages.
   - `progress --missed`: missed question text appears; empty state message
     otherwise.
3. Run the full `pytest` suite.

## 10. Decisions Left to the Builder

- Exact truncation width and styling for the missed-question column.
- Whether to sort domains canonically or by coverage (canonical is assumed).
- Table footer vs. summary line placement.
