# Design Specification: Unseen-First Study Mode & Web Simulator Statistics

**Date:** 2026-10-27  
**Status:** Approved  
**Scope:** CLI Exam Simulator (`gamb_exam`), SQLite Persistence Layer, and Single-File Web Simulator (`web/index.html`)

---

## 1. Overview and Goals

The Georgia Psychology Jurisprudence Examination Suite provides two primary question-answering modes:
1. **Timed Practice Exams (`test`)**: Realistic 50-question PSI exam simulations under time limits.
2. **Untimed Study Drills (`study`)**: Modular practice drills with immediate explanations and statutory citations.

Previously, `test` mode defaulted to prioritizing unseen questions, while `study` mode sampled completely at random without reference to past question history. This design aligns the modes with learner expectations:
- **`study` mode** prioritizes as-yet-unstudied questions by default, falling back gracefully to least-answered questions when unstudied items are exhausted, with an opt-out flag (`--no-unseen`).
- **`test` mode** defaults to realistic, unpredictable stratified random sampling across domains, with an opt-in flag (`--prioritize-unseen`) for users who explicitly want it.
- **Web Simulator (`web/index.html`)** gains synchronized study-drill unseen prioritization, a question coverage tracker, a dedicated **Stats Modal**, and clear/reset controls for study history and test sessions.

---

## 2. Architecture and Data Flow

### 2.1 CLI / SQLite Layer (`gamb_exam`)

```
[gamb-exam study] 
       │
       ▼
get_study_questions(domain, limit, prioritize_unseen=True)
       │
       ├──► SQLite: questions LEFT JOIN session_answers
       │    ORDER BY (CASE WHEN prioritize_unseen THEN times_answered ASC ELSE 1 END), RANDOM()
       │    LIMIT {limit}
       │
       ▼
shuffle_question_options() -> ExamApp(mode="study_drill")
```

### 2.2 Web Simulator Layer (`web/index.html`)

```
User answers question in PSI / Study Drill
       │
       ▼
recordQuestionAttempt(questionId, isCorrect)
       │
       ▼
storage.set('gamb_stats', JSON.stringify({ questions, sessions }))
       │
       ├──► Used by initDrillQuestions(): sorts unseen items first if prioritizeUnseen == true
       └──► Used by renderStatsModal(): displays coverage %, domain breakdowns, reset buttons
```

---

## 3. Detailed Component Specifications

### 3.1 Database Query Function (`gamb_exam/db.py`)

Add `get_study_questions`:
```python
def get_study_questions(
    domain: str | None = None,
    limit: int | None = 50,
    prioritize_unseen: bool = True,
    rng: random.Random | None = None,
    db_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve study questions, optionally filtered by domain and prioritized by unseen/least-answered status.

    When prioritize_unseen=True, questions answered fewer times across prior sessions
    appear before frequently answered questions, using random tie-breaking.
    If the number of completely unstudied questions is fewer than `limit`,
    questions with lowest answer counts backfill the remaining slots.
    """
```
- Query when `prioritize_unseen=True`:
  ```sql
  SELECT q.*, COUNT(sa.id) AS times_answered
  FROM questions q
  LEFT JOIN session_answers sa ON q.id = sa.question_id
  WHERE (? IS NULL OR q.domain = ?)
  GROUP BY q.id
  ORDER BY times_answered ASC, RANDOM()
  LIMIT ?
  ```
- Query when `prioritize_unseen=False`:
  ```sql
  SELECT q.*
  FROM questions q
  WHERE (? IS NULL OR q.domain = ?)
  ORDER BY RANDOM()
  LIMIT ?
  ```

### 3.2 Exam Generator (`gamb_exam/generator.py`)

- Update `generate_exam_questions`:
  - Change parameter default: `prioritize_unseen: bool = False` (was `True`).
  - Preserves domain quotas (`DOMAIN_QUOTAS`), 50-question stratification, and optional option-shuffling.

### 3.3 Command-Line Interface (`gamb_exam/cli.py`)

- **`study` parser**:
  - Add `--no-unseen` flag (`action="store_true"`, `default=False`, `help="Disable unseen question prioritization and sample randomly"`).
  - Update `handle_study`:
    ```python
    questions = get_study_questions(
        domain=args.domain,
        limit=args.count,
        prioritize_unseen=not args.no_unseen,
        db_path=args.db,
    )
    ```
- **`test` parser**:
  - Replace `--no-unseen` with `--prioritize-unseen` (`action="store_true"`, `default=False`, `help="Prioritize questions answered least often in prior sessions"`).
  - Update `handle_test`:
    ```python
    questions = generate_exam_questions(
        db_path=args.db,
        prioritize_unseen=args.prioritize_unseen,
        rng=rng,
    )
    ```

### 3.4 Web Simulator (`web/index.html`)

1. **Storage Schema (`gamb_stats`)**:
   ```javascript
   {
     "questions": {
       "1": { "timesAnswered": 2, "timesCorrect": 1, "lastAnswered": 1740000000000 },
       "2": { "timesAnswered": 1, "timesCorrect": 1, "lastAnswered": 1740000050000 }
     },
     "sessions": [
       { "id": 1, "mode": "psi", "score": 42, "total": 50, "passed": true, "timestamp": 1740000100000 }
     ]
   }
   ```
2. **Recording Hook**:
   - `recordQuestionAttempt(questionId, isCorrect)` invoked on answer selection in both PSI Exam and Study Drill modes.
   - `recordExamSession(score, total, passed)` invoked on PSI exam submission.
3. **Study Drill Question Selection**:
   - `state.drill.prioritizeUnseen` initialized to `true`.
   - In `initDrillQuestions()`:
     - Filter by selected domain (`all` or specific domain).
     - If `state.drill.prioritizeUnseen`:
       - Sort questions primarily by `timesAnswered` ascending (`stats.questions[q.id]?.timesAnswered || 0`), with random tie-break among questions with identical counts.
     - Else: standard Fisher-Yates random shuffle.
   - Add toolbar button next to Shuffle toggle:
     - `[Prioritize Unseen: ON]` / `[Prioritize Unseen: OFF]`.
4. **Stats Modal Component**:
   - Add `📊 Stats` button in the app header.
   - Modal contains:
     - **Summary Cards**: Total Bank (435), Studied Questions Count, % Bank Covered, Unstudied Remaining.
     - **Domain Coverage Grid**: For each of the 6 domains: progress bar of seen vs total questions, accuracy rate (% correct).
     - **Exam History Table**: List of recent PSI exams (Date, Score, Result PASS/FAIL).
     - **Management / Reset Buttons**:
       - `Reset Study Progress`: Resets question counters to 0 (with confirm dialog: *"Reset study progress? All questions will be treated as unseen."*).
       - `Clear All Data`: Clears question stats, exam session history, and missed question queue (with confirm dialog).
       - `Close`: Closes modal.

---

## 4. Error Handling and Edge Cases

- **Exhaustion of Unseen Questions**:
  - When `--count` (e.g. 50) exceeds remaining unseen questions in a domain (e.g. 10 left), `get_study_questions` automatically yields all 10 unseen questions first, followed by the 40 least-answered questions.
- **Empty Database / First Run**:
  - `ensure_db_initialized` initializes and seeds the database before question queries execute.
- **Browser Private Browsing / No LocalStorage**:
  - Existing `storage` wrapper safely falls back to in-memory store without crashing.
- **Backwards Compatibility**:
  - Existing databases and web sessions without `gamb_stats` initialize cleanly with empty object defaults.

---

## 5. Testing and Verification Plan

1. **Unit Tests (`tests/test_db.py`)**:
   - Verify `get_study_questions` returns all questions without errors.
   - Seed answers for select questions; verify `get_study_questions(prioritize_unseen=True)` returns zero-attempt questions before answered questions.
   - Verify `get_study_questions(prioritize_unseen=False)` does not sort by answer frequency.
   - Verify domain filtering and count limits.
2. **Generator Tests (`tests/test_generator.py`)**:
   - Verify default `generate_exam_questions()` runs with `prioritize_unseen=False`.
   - Verify passing `prioritize_unseen=True` orders by `times_answered ASC`.
3. **CLI Tests (`tests/test_cli.py`)**:
   - Test parser for `gamb-exam study --no-unseen`.
   - Test parser for `gamb-exam test --prioritize-unseen`.
4. **Web Simulator Validation**:
   - Test JS logic: storage helpers, recordQuestionAttempt, sort by unseen, modal open/close, reset callbacks.
5. **Full Regression Suite**:
   - Run `pytest` across all test files.
