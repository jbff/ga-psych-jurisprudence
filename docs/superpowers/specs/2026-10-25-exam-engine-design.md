# Design Specification: Georgia Psychology Jurisprudence Exam Engine & TUI Simulator

**Date:** 2026-10-25  
**Project:** Georgia Psychology Jurisprudence (GAMB) Exam Engine & Study Suite  
**Repository Target:** `jbff/ga-psych-jurisprudence` (GitHub, public, origin/master)

---

## 1. Overview & Purpose

The purpose of this project is to provide a complete, offline-capable, interactive terminal-based practice examination suite for candidates preparing for the **Georgia Psychology Jurisprudence Examination**. 

The suite transforms the verified 435-card Anki deck and primary Georgia legal corpus into a structured 4-option multiple-choice question (MCQ) pool, backed by an SQLite engine (`gamb_exam.db`), managed with `uv`, and rendered in the terminal via a full-screen, keyboard-driven Terminal User Interface (TUI) powered by `rich` and `textual`.

---

## 2. Environment & Dependency Management (`uv`)

All Python dependencies and virtual environments are strictly managed using **`uv`**:
* **Virtual Environment**: `.venv` initialized and maintained via `uv venv`.
* **Project Configuration**: `pyproject.toml` with console script entry points:
  - `gamb-exam = "gamb_exam.cli:main"`
* **Dependencies**:
  - `rich >= 13.0`
  - `textual >= 0.50.0`
* **Execution**: All tasks are runnable via `uv run gamb-exam <command>`.

---

## 3. Database Architecture (`data/gamb_exam.db`)

An SQLite database provides persistence for the question pool, user test sessions, individual answers, and historical domain performance.

### Schema:
```sql
-- 1. Question Pool
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL,           -- 'prof-relationships', 'licensure', 'competence', 'assessment', 'privacy', 'recordkeeping'
    subtopic TEXT,                  -- e.g., 'Mandated Child Abuse Reporting', 'Supervisory Ratio'
    source_citation TEXT NOT NULL,  -- e.g., 'OCGA § 19-7-5(e)', 'Rule 510-5-.06(3)(a)(5)'
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option TEXT NOT NULL,   -- 'A', 'B', 'C', or 'D'
    explanation TEXT NOT NULL,      -- Full statutory or administrative rule explanation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Practice Test Sessions
CREATE TABLE IF NOT EXISTS exam_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode TEXT NOT NULL,             -- 'timed_exam' (60 min) or 'study_drill' (untimed)
    total_questions INTEGER NOT NULL DEFAULT 50,
    score INTEGER,                  -- Number of correct answers
    percentage REAL,                -- Score percentage (0.0 - 100.0)
    passed BOOLEAN,                 -- TRUE if score >= 38
    time_spent_seconds INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 3. Detailed Question Responses
CREATE TABLE IF NOT EXISTS session_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES exam_sessions(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questions(id),
    selected_option TEXT,           -- 'A', 'B', 'C', 'D' or NULL if skipped
    is_correct BOOLEAN NOT NULL,
    flagged BOOLEAN DEFAULT FALSE,
    time_spent_seconds INTEGER
);
```

---

## 4. Question Pool & Distractor Generation Strategy

1. **Source Material**:
   - The 435 verified cards in `anki/gamb_deck.tsv`.
   - The unabridged primary statutes in `study_corpus/STATUTES_OC_GA.md`.
   - The complete Board Rules in `study_corpus/RULES_510_FULL.md`.
2. **Distractor Quality & Realism**:
   - For every question stem, three plausible, legally coherent distractors are generated reflecting authentic statutory variations in Georgia law (e.g. contrasting 24 hours vs. 48 hours vs. 72 hours; misdemeanor vs. felony; DFCS vs. Adult Protective Services; 3-supervisee limit vs. 2 or 4; $500 fine vs. $1,000 fine).
   - Distractors never use obvious absurdities ("None of the above", "All of the above" are avoided where possible).
3. **Randomized Key Distribution**:
   - Correct options are distributed uniformly across A, B, C, and D.
4. **Seed Database Script**:
   - A dedicated population script (`gamb_exam/seed.py`) reads the curated question dataset and populates `data/gamb_exam.db`.

---

## 5. Stratified 50-Question Exam Generator

When a practice test is started, the generator pulls a stratified random sample adhering exactly to the official Board specifications:

| Domain | Outline Item Count | Percentage | Pool Allocation |
|:---|:---:|:---:|:---:|
| **Professional Relationships** | **14 questions** | 28% | Sampled from `prof-relationships` |
| **Licensure and Regulations** | **13 questions** | 26% | Sampled from `licensure` |
| **Competence** | **9 questions** | 18% | Sampled from `competence` |
| **Assessment** | **6 questions** | 12% | Sampled from `assessment` |
| **Privacy and Confidentiality** | **5 questions** | 10% | Sampled from `privacy` |
| **Recordkeeping and Fees** | **3 questions** | 6% | Sampled from `recordkeeping` |
| **Total Exam** | **50 questions** | **100%** | **Passing = 38 / 50 (76%)** |

### Sampling Logic:
* **Unseen Prioritization**: Prioritizes questions least recently answered or unanswered in past sessions.
* **No In-Exam Duplication**: Exactly 50 unique questions per exam.
* **Option Shuffling**: Dynamic option letter shuffling per session to eliminate memorizing option positions.

---

## 6. Terminal User Interface (TUI) & Feature Modes

### A. Timed Exam Mode (`uv run gamb-exam test`)
* **Time Limit**: 60-minute countdown timer displayed prominently in the header bar.
* **Navigation**:
  - `[N]` or `[Enter]`: Next question.
  - `[P]`: Previous question.
  - `[F]`: Flag question for review.
  - `[J]`: Jump to question grid (visual indicator of answered, unanswered, flagged questions).
  - `[S]`: Submit test (warns if unanswered questions remain).
* **Final Diagnostics**:
  - Overall Score: Pass/Fail badge against 38/50 (76%).
  - Domain Breakdown Table with item counts and pass/fail indicators.
  - Interactive Review: Walk through all questions or only missed questions with full explanations.

### B. Study Drill Mode (`uv run gamb-exam study`)
* Untimed mode.
* Selecting an answer immediately reveals whether it is correct/incorrect, shows the correct option, statutory citation, and in-depth explanation before advancing.

### C. Missed Items Drill (`uv run gamb-exam missed`)
* Queries `session_answers` for questions answered incorrectly in previous sessions.
* Enables targeted drills until mastery is reached.

### D. History & Statistics (`uv run gamb-exam stats`)
* Displays overall historical performance, total exams taken, pass rate, and domain-by-domain mastery percentages.

### E. Mock Export (`uv run gamb-exam export`)
* Exports the current 50-question generated test and its corresponding answer key into `mocks/mock_YYYY-MM-DD_HHMM.md` for offline study or printing.

---

## 7. Git & GitHub Repository Management

1. **Repository Setup**:
   - Git repository initialized in `/sto/hom/gamb`.
   - Default branch: `master`.
   - Remote: `origin` pointing to `git@github.com:jbff/ga-psych-jurisprudence.git` (or HTTPS equivalent).
   - Public GitHub repository created via `gh repo create jbff/ga-psych-jurisprudence --public --source=. --remote=origin`.
2. **Push Workflow**:
   - All commits are pushed to `origin/master`.
3. **Repository Structure**:
   - `study_corpus/` — Clean, unabridged statutory and rule sources.
   - `corpus_combined/` — Consolidated source files.
   - `sources/` — Raw underlying legal and bulletin files.
   - `anki/` — Spaced-repetition Anki deck (435 cards) and import guide.
   - `mocks/` — Pre-built and generated 50-Q mock exams.
   - `gamb_exam/` — The Python package (TUI, database, generator, CLI).
   - `data/` — SQLite database and JSON seed files.
   - `README.md` & `LICENSE` — Project documentation and legal disclaimer.

---

## 8. Prominent Legal Disclaimer

The repository and CLI application will prominently feature the following disclaimer:

> **LEGAL DISCLAIMER & NOTICE OF NON-AFFILIATION**  
> *This study kit, question pool, flashcard deck, and exam simulator are independent, community-created educational tools. They are **NOT** official examination materials, and are neither affiliated with, authorized, sponsored, nor endorsed by the Georgia State Board of Examiners of Psychologists, the Georgia Secretary of State Professional Licensing Boards Division, the Association of State and Provincial Psychology Boards (ASPPB), or PSI Services LLC.*  
>  
> *All practice questions, scenarios, and distractors are original generated study aids created for self-assessment purposes and do NOT represent actual live examination items. All materials are provided "AS IS" without warranty of any kind, express or implied, including warranties of merchantability, fitness for a particular purpose, or accuracy. The authors and maintainers assume NO responsibility or legal liability for errors, omissions, or the user's performance on the Georgia Psychology Jurisprudence Examination. Using these materials does not guarantee a passing score, and no liability is accepted if a candidate fails the examination.*
