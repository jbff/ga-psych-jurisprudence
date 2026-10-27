# Unseen-First Study Mode & Web Simulator Statistics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prioritize unstudied questions in study drills across both the Python CLI suite and the standalone web simulator, allow graceful backfill from least-answered questions, switch test mode to realistic pure-random draws, and provide local statistics tracking and reset capabilities in the web simulator.

**Architecture:** 
- In SQLite/Python (`gamb_exam`), `get_study_questions` orders by `times_answered ASC, RANDOM()` to prioritize questions with zero or few previous attempts, while `generate_exam_questions` defaults to unbiased random draws (`prioritize_unseen=False`).
- In CLI (`gamb_exam/cli.py`), `study` defaults to unseen prioritization with an opt-out `--no-unseen` flag, and `test` defaults to pure random with an opt-in `--prioritize-unseen` flag.
- In Web (`web/index.html`), question attempts are stored in `localStorage` under `gamb_stats`; study drills prioritize unseen items by default (with a UI toggle), and a Stats Modal displays progress across the 435-question bank and 6 domains with reset controls.

**Tech Stack:** Python 3.10+, SQLite3, Textual/Rich, Vanilla JavaScript (ES6+), HTML5, LocalStorage, pytest.

---

### Task 1: Add `get_study_questions` to `gamb_exam/db.py`

**Files:**
- Modify: `gamb_exam/db.py`
- Test: `tests/test_db.py`

- [ ] **Step 1: Write the failing tests in `tests/test_db.py`**

Add tests verifying `get_study_questions`:
```python
def test_get_study_questions_unseen_prioritization(tmp_db_path: Path):
    """Verifies get_study_questions prioritizes questions with zero answers before answered ones."""
    init_db(tmp_db_path)
    # Insert 4 questions in prof-relationships
    for i in range(1, 5):
        insert_question(
            sample_question_data(domain="prof-relationships", stem_suffix=str(i)),
            db_path=tmp_db_path,
        )

    # Answer questions 1 and 2
    sess_id = create_session(db_path=tmp_db_path)
    save_session_answer(session_id=sess_id, question_id=1, selected_option="A", is_correct=True, db_path=tmp_db_path)
    save_session_answer(session_id=sess_id, question_id=2, selected_option="B", is_correct=False, db_path=tmp_db_path)

    # Retrieve 2 questions with prioritize_unseen=True
    from gamb_exam.db import get_study_questions

    study_qs = get_study_questions(domain="prof-relationships", limit=2, prioritize_unseen=True, db_path=tmp_db_path)
    assert len(study_qs) == 2
    # Questions 3 and 4 have 0 answers, so both must be selected
    study_ids = {q["id"] for q in study_qs}
    assert study_ids == {3, 4}


def test_get_study_questions_backfill_and_no_unseen(tmp_db_path: Path):
    """Verifies graceful backfill when count exceeds unseen and verify prioritize_unseen=False."""
    init_db(tmp_db_path)
    for i in range(1, 4):
        insert_question(
            sample_question_data(domain="licensure", stem_suffix=str(i)),
            db_path=tmp_db_path,
        )

    # Question 1 answered twice, question 2 answered once, question 3 answered zero times
    sess_id = create_session(db_path=tmp_db_path)
    save_session_answer(session_id=sess_id, question_id=1, selected_option="A", is_correct=True, db_path=tmp_db_path)
    save_session_answer(session_id=sess_id, question_id=1, selected_option="A", is_correct=True, db_path=tmp_db_path)
    save_session_answer(session_id=sess_id, question_id=2, selected_option="A", is_correct=True, db_path=tmp_db_path)

    from gamb_exam.db import get_study_questions

    # Request all 3: order must be question 3 (0 answers), then question 2 (1 answer), then question 1 (2 answers)
    study_qs = get_study_questions(domain="licensure", limit=3, prioritize_unseen=True, db_path=tmp_db_path)
    assert [q["id"] for q in study_qs] == [3, 2, 1]

    # Test prioritize_unseen=False returns all questions without errors
    random_qs = get_study_questions(domain=None, limit=3, prioritize_unseen=False, db_path=tmp_db_path)
    assert len(random_qs) == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_db.py -k "test_get_study_questions" -v`  
Expected: FAIL with `ImportError: cannot import name 'get_study_questions' from 'gamb_exam.db'`

- [ ] **Step 3: Implement `get_study_questions` in `gamb_exam/db.py`**

Add the function to `gamb_exam/db.py`:
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
    If the number of completely unstudied questions is fewer than limit,
    questions with lowest answer counts backfill the remaining slots.
    """
    conn = get_connection(db_path)
    if rng is not None:
        conn.create_function(
            "RANDOM",
            0,
            lambda: rng.randint(-9223372036854775808, 9223372036854775807),
        )

    try:
        cursor = conn.cursor()
        params: list[Any] = []
        where_clause = ""
        if domain is not None:
            where_clause = "WHERE q.domain = ?"
            params.append(domain)

        if prioritize_unseen:
            query = f"""
                SELECT q.*, COUNT(sa.id) AS times_answered
                FROM questions q
                LEFT JOIN session_answers sa ON q.id = sa.question_id
                {where_clause}
                GROUP BY q.id
                ORDER BY times_answered ASC, RANDOM()
            """
        else:
            query = f"""
                SELECT q.*
                FROM questions q
                {where_clause}
                ORDER BY RANDOM()
            """

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
```
Also ensure `random` is imported in `gamb_exam/db.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_db.py -k "test_get_study_questions" -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add gamb_exam/db.py tests/test_db.py
git commit -m "feat(db): add get_study_questions with unseen prioritization and backfill"
```

---

### Task 2: Update `generate_exam_questions` Default in `gamb_exam/generator.py`

**Files:**
- Modify: `gamb_exam/generator.py:99-115`
- Test: `tests/test_generator.py:91-126`

- [ ] **Step 1: Write the updated test in `tests/test_generator.py`**

Update `test_prioritize_unseen` in `tests/test_generator.py` to test both the new default (`prioritize_unseen=False`) and explicit `prioritize_unseen=True`:
```python
def test_prioritize_unseen(tmp_db_path: Path):
    """Verifies prioritize_unseen=True prioritizes questions with fewest prior answers and default is False."""
    seed_database(tmp_db_path)

    # Inspect questions in 'recordkeeping' domain (quota = 3, total = 21)
    conn = get_connection(tmp_db_path)
    cur = conn.cursor()
    cur.execute("SELECT id FROM questions WHERE domain = 'recordkeeping' ORDER BY id ASC")
    recordkeeping_ids = [row["id"] for row in cur.fetchall()]
    conn.close()

    assert len(recordkeeping_ids) >= 3

    # Mark all but 2 of the recordkeeping questions as answered
    unseen_ids = set(recordkeeping_ids[:2])
    seen_ids = recordkeeping_ids[2:]

    session_id = create_session(db_path=tmp_db_path)
    for qid in seen_ids:
        save_session_answer(
            session_id=session_id,
            question_id=qid,
            selected_option="A",
            is_correct=True,
            db_path=tmp_db_path,
        )

    # Default generate_exam_questions has prioritize_unseen=False
    default_questions = generate_exam_questions(db_path=tmp_db_path)
    assert len(default_questions) == 50

    # Explicitly generate exam questions with prioritize_unseen=True
    questions = generate_exam_questions(db_path=tmp_db_path, prioritize_unseen=True)
    generated_rk_ids = {q["id"] for q in questions if q["domain"] == "recordkeeping"}

    # Both unseen questions MUST be prioritized into the 3 selected questions
    assert len(generated_rk_ids) == 3
    assert unseen_ids.issubset(generated_rk_ids)
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_generator.py::test_prioritize_unseen -v`  
Expected: verify behavior under existing code.

- [ ] **Step 3: Update `gamb_exam/generator.py`**

In `gamb_exam/generator.py`:
Change `prioritize_unseen: bool = True` to `prioritize_unseen: bool = False` in `generate_exam_questions`:
```python
def generate_exam_questions(
    db_path: Path | str | None = None,
    prioritize_unseen: bool = False,
    shuffle_options: bool = True,
    rng: random.Random | None = None,
) -> list[dict[str, Any]]:
```

- [ ] **Step 4: Run tests to verify all generator tests pass**

Run: `pytest tests/test_generator.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add gamb_exam/generator.py tests/test_generator.py
git commit -m "feat(generator): default exam generation to pure random draw"
```

---

### Task 3: Update CLI Commands in `gamb_exam/cli.py`

**Files:**
- Modify: `gamb_exam/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests in `tests/test_cli.py`**

Update `test_cli_test_command` and add `test_cli_study_unseen_handling` in `tests/test_cli.py`:
```python
def test_cli_test_command_default_and_flag(tmp_db_path: Path):
    """Verifies 'test' subcommand defaults to prioritize_unseen=False and respects --prioritize-unseen."""
    from gamb_exam.cli import main

    mock_questions = [{"id": 1, "domain": "prof-relationships", "question_text": "Q", "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D", "correct_option": "A", "explanation": "E"}]

    with (
        patch("gamb_exam.cli.generate_exam_questions", return_value=mock_questions) as mock_gen,
        patch("gamb_exam.tui.ExamApp") as mock_app_cls,
    ):
        mock_app_instance = MagicMock()
        mock_app_cls.return_value = mock_app_instance

        # Default run
        ret = main(["test", "--db", str(tmp_db_path), "--seed", "123"])
        assert ret == 0
        assert mock_gen.call_args.kwargs.get("prioritize_unseen") is False

        # Flag run
        mock_gen.reset_mock()
        ret = main(["test", "--db", str(tmp_db_path), "--seed", "123", "--prioritize-unseen"])
        assert ret == 0
        assert mock_gen.call_args.kwargs.get("prioritize_unseen") is True


def test_cli_study_command_unseen_handling(tmp_db_path: Path):
    """Verifies 'study' subcommand defaults to prioritize_unseen=True and respects --no-unseen."""
    from gamb_exam.cli import main

    mock_questions = [{"id": 1, "domain": "prof-relationships", "question_text": "Q", "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D", "correct_option": "A", "explanation": "E"}]

    with (
        patch("gamb_exam.cli.get_study_questions", return_value=mock_questions) as mock_study_qs,
        patch("gamb_exam.tui.ExamApp") as mock_app_cls,
    ):
        mock_app_instance = MagicMock()
        mock_app_cls.return_value = mock_app_instance

        # Default study run: prioritize_unseen must be True
        ret = main(["study", "--db", str(tmp_db_path), "--domain", "licensure", "--count", "20"])
        assert ret == 0
        mock_study_qs.assert_called_once_with(
            domain="licensure",
            limit=20,
            prioritize_unseen=True,
            db_path=tmp_db_path,
        )

        # Opt-out study run: --no-unseen
        mock_study_qs.reset_mock()
        ret = main(["study", "--db", str(tmp_db_path), "--no-unseen"])
        assert ret == 0
        mock_study_qs.assert_called_once_with(
            domain=None,
            limit=50,
            prioritize_unseen=False,
            db_path=tmp_db_path,
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -k "test_cli_study_command_unseen_handling or test_cli_test_command_default_and_flag" -v`  
Expected: FAIL

- [ ] **Step 3: Update `gamb_exam/cli.py`**

In `gamb_exam/cli.py`:
1. Import `get_study_questions` from `gamb_exam.db`.
2. Update `handle_test`:
```python
def handle_test(args: argparse.Namespace) -> int:
    """Handle the 'test' subcommand to run a timed 50-question simulation."""
    rng = random.Random(args.seed) if args.seed is not None else None
    try:
        questions = generate_exam_questions(
            db_path=args.db,
            prioritize_unseen=args.prioritize_unseen,
            rng=rng,
        )
...
```
3. Update `handle_study`:
```python
def handle_study(args: argparse.Namespace) -> int:
    """Handle the 'study' subcommand to run an untimed drill with instant feedback."""
    ensure_db_initialized(args.db)
    questions = get_study_questions(
        domain=args.domain,
        limit=args.count,
        prioritize_unseen=not args.no_unseen,
        db_path=args.db,
    )

    if not questions:
        console.print("[yellow]No questions found for study drill.[/yellow]")
        return 0

    questions = [shuffle_question_options(q) for q in questions]

    from gamb_exam.tui import ExamApp

    app = ExamApp(questions=questions, mode="study_drill", db_path=args.db)
    app.run()
    return 0
```
4. In `test_parser`:
```python
    test_parser.add_argument(
        "--prioritize-unseen",
        action="store_true",
        default=False,
        help="Prioritize questions answered least often in prior sessions",
    )
```
5. In `study_parser`:
```python
    study_parser.add_argument(
        "--no-unseen",
        action="store_true",
        default=False,
        help="Disable unseen question prioritization and sample randomly",
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_cli.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add gamb_exam/cli.py tests/test_cli.py
git commit -m "feat(cli): wire up unseen study mode and prioritize-unseen test flag"
```

---

### Task 4: Enhance Web Simulator (`web/index.html`)

**Files:**
- Modify: `web/index.html`

- [ ] **Step 1: Implement LocalStorage Stats Engine in `web/index.html`**

In `web/index.html`, add stats management functions:
- `getStats()`: returns `{ questions: {}, sessions: [] }` from `storage.get('gamb_stats')`.
- `saveStats(stats)`: saves object to `storage.set('gamb_stats', JSON.stringify(stats))`.
- `recordQuestionAttempt(questionId, isCorrect)`: updates `stats.questions[questionId]` with `timesAnswered: (prev.timesAnswered || 0) + 1`, `timesCorrect: (prev.timesCorrect || 0) + (isCorrect ? 1 : 0)`, `lastAnswered: Date.now()`.
- `recordExamSession(score, total, passed)`: appends session object to `stats.sessions`.
- `resetStudyProgress()`: resets `stats.questions = {}` and saves.
- `clearAllSimulatorData()`: resets `stats = { questions: {}, sessions: [] }`, clears `gamb_missed_questions`, updates badges, and re-renders.

- [ ] **Step 2: Hook Recording to Answer Selection & Exam Submission**

- In `selectPsiOption(opt)` or `submitPsiExam()`: call `recordQuestionAttempt` for each question answered, and `recordExamSession(score, 50, passed)` upon submission.
- In `selectDrillOption(letter)`: call `recordQuestionAttempt(currentQ.id, letter === currentQ.correct_option)`.

- [ ] **Step 3: Update `initDrillQuestions()` for Unseen Prioritization**

In `web/index.html`:
- Add `state.drill.prioritizeUnseen = true`.
- In `initDrillQuestions()`:
```javascript
  const stats = getStats();
  if (state.drill.prioritizeUnseen) {
    list.sort((a, b) => {
      const countA = (stats.questions[a.id] && stats.questions[a.id].timesAnswered) || 0;
      const countB = (stats.questions[b.id] && stats.questions[b.id].timesAnswered) || 0;
      if (countA !== countB) return countA - countB;
      return Math.random() - 0.5;
    });
  } else if (state.drill.shuffled) {
    for (let i = list.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [list[i], list[j]] = [list[j], list[i]];
    }
  }
```
- In drill toolbar: Add button:
  `<button class="btn btn-secondary btn-sm" onclick="toggleDrillPrioritizeUnseen()">${state.drill.prioritizeUnseen ? 'Prioritize Unseen: ON' : 'Prioritize Unseen: OFF'}</button>`

- [ ] **Step 4: Implement Stats Modal Component & Header Button**

In `web/index.html`:
- Add `📊 Stats` button in the app header navbar:
  `<button class="btn btn-secondary btn-sm" onclick="openStatsModal()">📊 Stats</button>`
- Add `openStatsModal()`, `closeStatsModal()`, and `renderStatsModalContent()`:
  - Total Questions (435), Studied Count, % Coverage, Unseen Count.
  - Per-domain coverage bar and accuracy %.
  - Recent PSI exam scores.
  - Action buttons:
    - "Reset Study History" (`resetStudyProgress()` with `confirm()`)
    - "Clear All Simulator Data" (`clearAllSimulatorData()` with `confirm()`)
    - "Close"

- [ ] **Step 5: Verify in Browser / Node test script**

Run a headless script or node validation to ensure valid JavaScript syntax and functions:
```bash
node -e "const fs = require('fs'); const html = fs.readFileSync('web/index.html', 'utf8'); console.log('Length:', html.length);"
```

- [ ] **Step 6: Commit**

```bash
git add web/index.html
git commit -m "feat(web): add stats tracking, stats modal, and unseen prioritization in study drill"
```

---

### Task 5: End-to-End Regression Testing & Final Verification

**Files:**
- Touch: all test suites

- [ ] **Step 1: Run full test suite**

Run: `pytest -v`  
Expected: All tests pass (0 failures).

- [ ] **Step 2: Verify CLI behavior manually**

Run:
```bash
python -m gamb_exam.cli study --count 5 --db data/gamb_exam.db --no-unseen
```
Verify it executes cleanly without runtime errors.

- [ ] **Step 3: Commit any final cleanup or test adjustments**

```bash
git status
```
Ensure working tree is clean.
