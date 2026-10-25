# Curated Question Pool Audit & Distractor Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Overhaul the entire 435-question pool for the Georgia Psychology Jurisprudence Examination, replacing synthetic domain-fallback guessing with human-grade, context-responsive, and legally plausible distractors stored in `gamb_exam/question_pool.json`, auto-seeded into SQLite, and strictly verified by automated tests.

**Architecture:** A static, version-controlled JSON dataset (`gamb_exam/question_pool.json`) housing all 435 audited questions with 4 distinct, semantically congruous options (A–D), verified single correct answer, and statutory explanations. `gamb_exam/seed.py` loads this curated bank into SQLite (`data/gamb_exam.db`) on demand, with dynamic per-exam option shuffling preserved in `generator.py`.

**Tech Stack:** Python 3.10+, `sqlite3`, `pytest`, `json`, `uv`, `git`.

---

### Task 1: Question Pool Test Suite & Engine Scaffolding

**Files:**
- Create: `tests/test_question_pool.py`
- Modify: `gamb_exam/seed.py`

- [x] **Step 1: Write comprehensive question pool validation tests (`tests/test_question_pool.py`)**

Write unit tests verifying:
1. `gamb_exam/question_pool.json` exists and parses cleanly.
2. Contains exactly 435 question objects.
3. Every question has integer `id` (1 through 435, all unique).
4. `domain` is one of `{"prof-relationships", "licensure", "competence", "assessment", "privacy", "recordkeeping"}`.
5. `source_citation`, `question_text`, and `explanation` are non-empty strings.
6. `options` has exactly 4 keys (`"A"`, `"B"`, `"C"`, `"D"`).
7. All 4 option strings are non-empty and mutually distinct (ignoring whitespace and trailing punctuation).
8. `correct_option` is in `{"A", "B", "C", "D"}`.
9. Semantic check: If stem asks "Who", options do not contain quantities like "hours" or "supervisees".
10. `seed_database()` correctly imports from `question_pool.json` into SQLite.

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_question_pool.py`  
Expected: FAIL (`FileNotFoundError: gamb_exam/question_pool.json` or empty).

- [x] **Step 3: Update `gamb_exam/seed.py` to support `question_pool.json`**

Update `gamb_exam/seed.py`:
- `QUESTION_POOL_JSON = Path(__file__).parent / "question_pool.json"`
- If `QUESTION_POOL_JSON.exists()`, `build_question_records()` loads directly from JSON.
- Fallback to TSV parser if JSON does not exist.

- [x] **Step 4: Commit scaffolding**

```bash
git add gamb_exam/seed.py tests/test_question_pool.py
git commit -m "test(pool): add question pool integrity test suite and seed loader"
```

---

### Task 2: Audit Licensure & Regulations (Questions 1–185)

**Files:**
- Modify: `gamb_exam/question_pool.json` (generate/update items 1–185)

- [x] **Step 1: Audit and generate items 1–60 (Batch 1: Licensure Requirements & Board Powers)**
Apply distractor standards to items 1–60 (EPPP, GAMB, oral exam, board appointments, terms, qualifications, postdoctoral hours, out-of-state practice).
Ensure every distractor responds to the question stem with plausible regulatory alternatives.

- [x] **Step 2: Audit and generate items 61–120 (Batch 2: Board Rules & Disciplinary Actions)**
Apply distractor standards to items 61–120 (administrative hearings, subpoena powers, judicial appeals, APA procedures, civil fines, grounds for denial).

- [x] **Step 3: Audit and generate items 121–185 (Batch 3: Telepsychology & Drug Sanctions)**
Apply distractor standards to items 121–185 (PSYPACT, telepsychology standards, emergency temporary practice, drug offense sanctions minimum vs. maximum, reinstatement conditions).

- [x] **Step 4: Verify items 1–185**

Run automated check on items 1–185 to verify 4 distinct options, 1 correct answer, and semantic responsiveness.

- [x] **Step 5: Commit**

```bash
git add gamb_exam/question_pool.json
git commit -m "feat(pool): audit and curate Licensure & Regulations questions (1-185)"
```

---

### Task 3: Audit Professional Relationships (Questions 186–258)

**Files:**
- Modify: `gamb_exam/question_pool.json` (update items 186–258)

- [x] **Step 1: Audit and generate items 186–225 (Batch 4: Supervisory Ratios & Boundaries)**
Apply distractor standards to items 186–225 (maximum supervisee limits, supervisor qualifications, written supervision plans, evaluation responsibilities, multiple relationships, informed consent).

- [x] **Step 2: Audit and generate items 226–258 (Batch 5: Sexual Misconduct Criminal Penalties & Mandatory Reporting)**
Apply distractor standards to items 226–258 (O.C.G.A. § 16-6-5.1 first and second degree improper sexual contact, victim consent not a defense, penalties, reporting colleagues, child abuse reporting § 19-7-5).

- [x] **Step 3: Verify items 186–258**

Run automated check on items 186–258 to verify option validity and responsiveness.

- [x] **Step 4: Commit**

```bash
git add gamb_exam/question_pool.json
git commit -m "feat(pool): audit and curate Professional Relationships questions (186-258)"
```

---

### Task 4: Audit Competence (Questions 259–362)

**Files:**
- Modify: `gamb_exam/question_pool.json` (update items 259–362)

- [x] **Step 1: Audit and generate items 259–310 (Batch 6: Scope of Practice & Continuing Education)**
Apply distractor standards to items 259–310 (40 CE credits per biennium, 6 ethics hours, Area I vs. Area II limits, competence boundaries, consulting specialists, delegating duties).

- [x] **Step 2: Audit and generate items 311–362 (Batch 7: Impairment, Emergency Commitment & Hospital Privileges)**
Apply distractor standards to items 311–362 (O.C.G.A. § 37-3-41 Form 1013 involuntary examination authority, peace officer duties, hospital practice § 31-7-164, mental/physical incompetence evaluations).

- [x] **Step 3: Verify items 259–362**

Run automated check on items 259–362 to verify option validity and responsiveness.

- [x] **Step 4: Commit**

```bash
git add gamb_exam/question_pool.json
git commit -m "feat(pool): audit and curate Competence questions (259-362)"
```

---

### Task 5: Audit Assessment, Privacy, & Recordkeeping (Questions 363–435)

**Files:**
- Modify: `gamb_exam/question_pool.json` (update items 363–435)

- [ ] **Step 1: Audit and generate items 363–392 (Batch 8: Psychological Assessment & Testing)**
Apply distractor standards to items 363–392 (O.C.G.A. § 43-39-1 definition of psychological testing, test security, raw data release vs. test protocols, third-party observers, obsolete tests, computerized interpretations).

- [ ] **Step 2: Audit and generate items 393–414 (Batch 9A: Privacy, Confidentiality, & Privilege)**
Apply distractor standards to items 393–414 (O.C.G.A. § 43-39-16 attorney-client privilege level, exceptions, court-ordered evaluations, Bradley Center duty to warn, elder abuse § 30-5-4 privilege override).

- [ ] **Step 3: Audit and generate items 415–435 (Batch 9B: Recordkeeping & Fees)**
Apply distractor standards to items 415–435 (7-year adult record retention, minor records to age 22 / 7 years, financial arrangements, fee disputes, collection agencies, withholding records for nonpayment).

- [ ] **Step 4: Verify complete pool (all 435 questions)**

Run: `uv run pytest tests/test_question_pool.py`  
Expected: 100% PASS across all 435 questions.

- [ ] **Step 5: Commit**

```bash
git add gamb_exam/question_pool.json
git commit -m "feat(pool): audit and curate Assessment, Privacy, and Recordkeeping questions (363-435)"
```

---

### Task 6: Full Integration, End-to-End Verification, & Remote Push

**Files:**
- Modify: `README.md`
- Verify: `mocks/`

- [ ] **Step 1: Re-seed local database and run full test suite**

Run:
```bash
rm -f data/gamb_exam.db
uv run pytest
```
Expected: 100% PASS across all 48+ unit, TUI, CLI, and pool tests.

- [ ] **Step 2: Re-export mock exams**

Run:
```bash
uv run gamb-exam export --output mocks/
```
Verify generated `mock_questions.md` and `mock_key.md` feature authentic, plausible distractors across all 50 questions.

- [ ] **Step 3: Update documentation**

Update `README.md` to note the curated 435-question pool with quality guarantees.

- [ ] **Step 4: Commit and push to GitHub `origin/master`**

```bash
git add .
git commit -m "feat(pool): complete 435-question bank audit with authentic distractors and update mocks"
git push origin master
```
