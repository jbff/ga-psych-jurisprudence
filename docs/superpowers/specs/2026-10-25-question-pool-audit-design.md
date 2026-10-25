# Specification: Curated Question Bank Audit & Distractor Overhaul

## 1. Objective & Problem Statement
During practice testing, several dynamically generated multiple-choice questions contained distractors drawn from unrelated domain flashcards that did not plausibly respond to the question asked (e.g. asking *"Are drug sanctions minimum or maximum?"* with distractors mentioning *"18 semester hours"* or *"Aid prosecuting attorneys"*).

To provide an authentic, high-yield practice testing experience, **every multiple choice distractor must be a conceivable, plausible answer to the specific question asked**, and **only one single answer must be legally correct** under Georgia psychology jurisprudence.

---

## 2. Architecture & Data Flow

1. **Permanent Curated Storage (`gamb_exam/question_pool.json`)**:
   - The question pool will be permanently stored as a version-controlled, human-audited JSON dataset at `gamb_exam/question_pool.json`.
   - Each entry contains:
     - `id`: Integer (1 to 435)
     - `domain`: One of the 6 official Board domains
     - `subtopic`: Detailed statutory/rule subtopic
     - `source_citation`: Specific O.C.G.A. statute or Board Rule citation
     - `question_text`: Complete question stem
     - `options`: Dictionary mapping `"A"`, `"B"`, `"C"`, `"D"` to distinct option strings
     - `correct_option`: `"A"`, `"B"`, `"C"`, or `"D"`
     - `explanation`: Full statutory citation and legal explanation

2. **Database Auto-Seeding (`gamb_exam/seed.py` & `gamb_exam/db.py`)**:
   - `gamb_exam/seed.py` will read directly from `gamb_exam/question_pool.json` to populate the local SQLite database (`data/gamb_exam.db`).
   - `ensure_db_initialized()` loads from `gamb_exam/question_pool.json`, guaranteeing that every practice test uses curated, plausible distractors without any runtime guesswork.
   - Dynamic per-exam option shuffling (`shuffle_question_options`) will continue to permute answer positions A–D so candidates cannot memorize letter keys.

---

## 3. Distractor Quality & Responsiveness Standards

Every question in `gamb_exam/question_pool.json` must adhere strictly to these rules:

1. **Semantic & Grammatical Congruity**:
   - Every option must directly respond to the grammatical interrogative of the stem:
     - **Who questions** -> Authorized entities/roles only (e.g. Governor, Board President, Administrative Law Judge, DFCS Case Worker).
     - **Timeframe / Deadline questions** -> Durations in identical units (e.g. 10 days, 30 days, 60 days, 90 days).
     - **Polar / Standard questions** -> Legal conditions, scopes, or standards (e.g. "Minimum; boards may impose more stringent sanctions", "Maximum; boards cannot exceed statutory limits").
     - **Penalty questions** -> Authentic Georgia penalties (e.g. High and aggravated misdemeanor, Felony 1–5 years, Revocation, $500 civil fine).
     - **Ratio / Count questions** -> Numerical quantities with identical units (e.g. 2 supervisees, 3 supervisees, 4 supervisees).

2. **Definitive Single Correct Answer**:
   - Exactly one answer is true under Georgia law.
   - Distractors must represent plausible legal alternatives, minority jurisdictions, or common candidate misunderstandings, but must be unambiguously incorrect under the cited Georgia statute or Board Rule.

3. **Homogeneous Tone & Length**:
   - Distractors must match the tone, length, and syntactic structure of the correct answer to prevent guessing based on option length or detail.

---

## 4. Audit Execution & Sample Verification Gate

### Step 1: 10-Question Representative Sample (Before vs. After)
Before auditing the entire pool, a representative 10-question sample spanning diverse question types will be presented to the user showing:
- Original Question Stem & Citation
- **Before**: Old options produced by procedural fallback
- **After**: New curated options adhering to the quality standards
- User approval is required before batch processing proceeds.

### Step 2: Batch Subagent Audit Pipeline
Once approved, the 435 questions will be audited across 9 domain batches:
- **Batch 1**: Licensure & Regulations (Part 1: Cards 1–60)
- **Batch 2**: Licensure & Regulations (Part 2: Cards 61–120)
- **Batch 3**: Licensure & Regulations (Part 3: Cards 121–185)
- **Batch 4**: Professional Relationships (Part 1: Cards 186–225)
- **Batch 5**: Professional Relationships (Part 2: Cards 226–258)
- **Batch 6**: Competence (Part 1: Cards 259–310)
- **Batch 7**: Competence (Part 2: Cards 311–362)
- **Batch 8**: Assessment (Cards 363–392, 30 cards)
- **Batch 9**: Privacy & Confidentiality (22 cards) & Recordkeeping & Fees (21 cards)

### Step 3: Automated Linter & Verification Gate
An automated test script (`tests/test_question_pool.py`) validates:
1. Total questions == 435.
2. All 435 IDs present and unique.
3. Every question has 4 non-empty, distinct options.
4. Correct option points to the exact statutory answer.
5. No trailing punctuation inconsistencies or duplicate options.
6. All 48 existing pytest suite tests continue to pass 100%.
