# Georgia Psychology Jurisprudence Exam Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete, offline-capable, interactive terminal-based 50-question practice exam suite for the Georgia Psychology Jurisprudence Examination, featuring a curated 4-choice question pool in SQLite, an exact-weighting stratified generator, a Rich/Textual TUI simulator, `uv` dependency management, and a public GitHub repository at `jbff/ga-psych-jurisprudence` with prominent disclaimers.

**Architecture:** A Python package (`gamb_exam`) backed by SQLite (`data/gamb_exam.db`), featuring a stratified sampler enforcing the Board's exact 6-domain distribution (14/13/9/6/5/3 = 50 Qs), and a full-screen, keyboard-navigated TUI (`textual` and `rich`) supporting Timed Exam, Study Drill, and Missed Items modes.

**Tech Stack:** Python 3.10+, `uv`, `sqlite3`, `rich`, `textual`, `pytest`, `git`, GitHub CLI (`gh`).

---

### Task 1: Git Repository & GitHub Remote Setup

**Files:**
- Create: `.gitignore`
- Create: `LICENSE`
- Modify: `README.md`

- [x] **Step 1: Initialize git repository and configure default branch to master**

Run:
```bash
git init -b master
```

- [x] **Step 2: Create .gitignore**

Write `.gitignore`:
```
.venv/
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
*.log
```

- [x] **Step 3: Create LICENSE with MIT terms and full legal disclaimer**

Write `LICENSE` including MIT terms and prominent non-affiliation / no-liability disclaimer for exam results.

- [x] **Step 4: Create remote repository on GitHub and set origin**

Run:
```bash
gh repo create jbff/ga-psych-jurisprudence --public --source=. --remote=origin || git remote add origin git@github.com:jbff/ga-psych-jurisprudence.git
```

- [x] **Step 5: Initial git commit**

Run:
```bash
git add .gitignore LICENSE README.md MANIFEST.md anki/ mocks/ study_corpus/ corpus_combined/ sources/ docs/
git commit -m "chore: initial commit of GA psychology jurisprudence study kit and specs"
```

---

### Task 2: Environment & Package Setup with `uv`

**Files:**
- Create: `pyproject.toml`
- Create: `gamb_exam/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [x] **Step 1: Create `pyproject.toml`**

Define project metadata, dependencies (`rich>=13.0`, `textual>=0.50.0`), dev dependencies (`pytest`), and console script entry point `gamb-exam = "gamb_exam.cli:main"`.

- [x] **Step 2: Create virtual environment and sync dependencies using `uv`**

Run:
```bash
uv venv
uv pip install rich textual pytest
```

- [x] **Step 3: Create basic package markers and test configuration**

Create `gamb_exam/__init__.py` (`__version__ = "1.0.0"`), `tests/__init__.py`, and `tests/conftest.py`.

- [x] **Step 4: Verify pytest works under `uv run`**

Run:
```bash
uv run pytest
```
Expected: `no tests ran in ...` (exited 5 or 0)

- [x] **Step 5: Commit**

```bash
git add pyproject.toml gamb_exam/__init__.py tests/
git commit -m "build: initialize uv environment and package configuration"
```

---

### Task 3: Database Engine & Schema (`gamb_exam/db.py`)

**Files:**
- Create: `gamb_exam/db.py`
- Test: `tests/test_db.py`

- [x] **Step 1: Write unit test for database initialization and CRUD operations**

Test `init_db(db_path)`, inserting a question, fetching by domain, and recording an exam session.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_db.py`  
Expected: `ModuleNotFoundError: No module named 'gamb_exam.db'`

- [x] **Step 3: Implement `gamb_exam/db.py`**

Implement `get_connection(db_path)`, `init_db(db_path)`, `insert_question(...)`, `create_session(...)`, `save_answers(...)`, and `get_history(...)`.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_db.py`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add gamb_exam/db.py tests/test_db.py
git commit -m "feat(db): implement SQLite database schema and session persistence"
```

---

### Task 4: Question Pool Population & Distractor Engine (`gamb_exam/seed.py`)

**Files:**
- Create: `gamb_exam/seed.py`
- Test: `tests/test_seed.py`

- [x] **Step 1: Write test for seed generation and question validity**

Verify that seed processing generates 4 distinct options (A, B, C, D) per question, with exactly one correct option, a non-empty explanation, and valid domain tags matching the 6 Board domains.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_seed.py`  
Expected: FAIL

- [x] **Step 3: Implement `gamb_exam/seed.py`**

Read `anki/gamb_deck.tsv`, transform the 435 cards into 4-choice questions with legally plausible distractors and code citations, and insert them into `data/gamb_exam.db`.

- [x] **Step 4: Run test to verify it passes and seed the database**

Run:
```bash
uv run pytest tests/test_seed.py
uv run python -m gamb_exam.seed
```
Expected: 435 questions inserted into `data/gamb_exam.db`.

- [x] **Step 5: Commit**

```bash
git add gamb_exam/seed.py tests/test_seed.py data/gamb_exam.db
git commit -m "feat(seed): generate 4-choice question pool and populate database"
```

---

### Task 5: Stratified 50-Question Exam Generator (`gamb_exam/generator.py`)

**Files:**
- Create: `gamb_exam/generator.py`
- Test: `tests/test_generator.py`

- [x] **Step 1: Write unit tests for stratified generation quotas and export**

Test:
1. Total questions == 50.
2. Exact domain distribution:
   - `prof-relationships`: exactly 14
   - `licensure`: exactly 13
   - `competence`: exactly 9
   - `assessment`: exactly 6
   - `privacy`: exactly 5
   - `recordkeeping`: exactly 3
3. Shuffled options and distinct questions.
4. Markdown export format.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_generator.py`  
Expected: FAIL

- [x] **Step 3: Implement `gamb_exam/generator.py`**

Implement `generate_exam_questions(db_path, prioritize_unseen=True)` and `export_mock_markdown(questions, output_dir="mocks")`.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_generator.py`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add gamb_exam/generator.py tests/test_generator.py
git commit -m "feat(generator): implement stratified 50-Q exam sampler and markdown exporter"
```

---

### Task 6: Terminal User Interface (TUI) Simulator (`gamb_exam/tui.py`)

**Files:**
- Create: `gamb_exam/tui.py`
- Test: `tests/test_tui.py`

- [x] **Step 1: Write smoke tests for TUI app instantiation and session state**

Verify `ExamApp` initializes with state, handles answer selection, navigation, and calculates score accurately.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_tui.py`  
Expected: FAIL

- [x] **Step 3: Implement `gamb_exam/tui.py`**

Implement Textual/Rich TUI:
- Header with countdown timer (60:00 for timed exam) and question tracker.
- Question stem & option selection (`[A]`, `[B]`, `[C]`, `[D]`).
- Instant explanation panel in Study Drill mode.
- Navigation bar (`[N] Next`, `[P] Prev`, `[F] Flag`, `[J] Jump`, `[S] Submit`).
- Diagnostic Score Report screen displaying overall pass/fail (vs. 38 cutoff) and 6-domain breakdown table.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_tui.py`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add gamb_exam/tui.py tests/test_tui.py
git commit -m "feat(tui): build full-screen Textual/Rich exam simulator and diagnostic reporter"
```

---

### Task 7: CLI Interface & Entry Points (`gamb_exam/cli.py`)

**Files:**
- Create: `gamb_exam/cli.py`
- Modify: `pyproject.toml`
- Test: `tests/test_cli.py`

- [x] **Step 1: Write CLI command tests**

Test `test`, `study`, `missed`, `stats`, and `export` subcommands.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py`  
Expected: FAIL

- [x] **Step 3: Implement `gamb_exam/cli.py`**

Implement CLI argument parser with subcommands:
- `test`: Run 60-min timed 50-Q exam.
- `study`: Run untimed study drill.
- `missed`: Drill questions missed in past sessions.
- `stats`: Print Rich table of cumulative historical scores & domain mastery.
- `export`: Generate balanced 50-Q mock markdown files in `mocks/`.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py`  
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add gamb_exam/cli.py tests/test_cli.py pyproject.toml
git commit -m "feat(cli): wire entry points and subcommands for exam suite"
```

---

### Task 8: Documentation, Full Verification, & GitHub Push

**Files:**
- Modify: `README.md`

- [x] **Step 1: Update `README.md` with full usage guide and prominent legal disclaimers**

Include:
- Quickstart with `uv run gamb-exam test`.
- Domain weighting breakdown table.
- Legal disclaimer of non-affiliation and zero liability.
- Anki deck instructions and study corpus guide.

- [x] **Step 2: Run complete test suite**

Run: `uv run pytest`  
Expected: 100% PASS across all unit and integration tests.

- [x] **Step 3: Test CLI end-to-end (export, stats)**

Run:
```bash
uv run gamb-exam export
uv run gamb-exam stats
```

- [x] **Step 4: Commit and push to GitHub `origin/master`**

Run:
```bash
git add .
git commit -m "docs: document exam engine, TUI usage, and legal disclaimers"
git push -u origin master
```
