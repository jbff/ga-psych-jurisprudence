# Georgia Psychology Jurisprudence Examination (GAMB) Study Kit & Simulator

> [!WARNING]
> **LEGAL & REGULATORY DISCLAIMER**:
> The study materials, question pools, flashcards, and practice exams contained in this repository are **independently generated study aids** and are **NOT official examination questions** from the Georgia State Board of Examiners of Psychologists, PSI Services LLC, or the Association of State and Provincial Psychology Boards (ASPPB). No guarantee, warranty, or representation is made regarding the accuracy, completeness, timeliness, or utility of these materials, or that studying them will result in a passing score on the Georgia Jurisprudence Examination (GAMB). Use of these materials is entirely at your own risk. The authors and contributors disclaim all liability for any claims, damages, direct or consequential losses, or examination failures arising from the use of or reliance upon these materials.

---

A comprehensive, rigorously audited jurisprudence examination study kit, printable PDF library, zero-install offline web quizzer, and interactive terminal simulator for psychologists preparing for the **Georgia Jurisprudence Examination (GAMB)** administered via PSI Services.

---

## 📦 Study Products & Downloads (No Installation Required)

Everything required to master the Georgia Jurisprudence Examination is packaged in ready-to-use, zero-dependency consumer formats. You do **not** need programming knowledge, Python, or command-line tools to start studying immediately. All study products are compiled from **Question Pool Version 1.0 (Release Date: 10/25/2026)**.

### Summary of Available Study Formats

| Product | Format | Description | Direct Access / Link |
| :--- | :---: | :--- | :--- |
| **Interactive Web Quizzer** | `index.html` | Timed 50-q PSI exam simulator, domain study drill, and missed question review. Runs 100% offline on any phone or laptop browser. | [web/index.html](web/index.html) |
| **Statutory Cheat Sheet** | `PDF` | High-yield 3-page summary of all critical numbers, CE caps, timeframes, penalties, and exceptions. | [Download Cheat Sheet PDF](pdfs/GAMB_Statutory_Cheat_Sheet.pdf) |
| **435-Question Compendium** | `PDF` | Complete self-study worktext organized by domain (Part I: Questions without answers; Part II: Back-of-book annotated key & citations). | [Download Compendium PDF](pdfs/GAMB_435_Question_Compendium.pdf) |
| **Practice Exam Form A** | `PDF` | 50-question mock exam booklet with instructions, bubble sheet, and annotated answer key in back. | [Download Form A PDF](pdfs/GAMB_Practice_Exam_Form_A.pdf) |
| **Practice Exam Form B** | `PDF` | 50-question mock exam booklet with instructions, bubble sheet, and annotated answer key in back. | [Download Form B PDF](pdfs/GAMB_Practice_Exam_Form_B.pdf) |
| **Practice Exam Form C** | `PDF` | 50-question mock exam booklet with instructions, bubble sheet, and annotated answer key in back. | [Download Form C PDF](pdfs/GAMB_Practice_Exam_Form_C.pdf) |
| **Anki Flashcard Deck** | `TSV` | 435 atomic flashcards for Anki, AnkiDroid, and AnkiMobile. | [anki/gamb_deck.tsv](anki/gamb_deck.tsv) |
| **Terminal Simulator (CLI/TUI)** | Python | Full PSI exam simulation for technical users and developers. | `uv run gamb-exam test` |

*(Note: Raw Markdown versions of all study guides and exam forms are also available in [`docs/study_materials/`](docs/study_materials/).)*

---

### 🌐 1. Interactive Web Quizzer (`web/index.html`)

A standalone, self-contained single-file web application with all 435 questions, distractors, legal rationales, and statutory citations embedded directly in the file. It runs completely offline with zero installation or external network requests.

- **How to Open Locally:**
  - Double-click [`web/index.html`](web/index.html) in your computer's file manager (Finder, Windows Explorer).
  - Or drag-and-drop `web/index.html` into Chrome, Safari, Firefox, or Edge.
  - Or from your browser menu, choose **File > Open File...** and select `web/index.html`.
- **How to Use on Phone or Tablet (iOS / Android):**
  - Transfer or AirDrop `web/index.html` to your iPhone, iPad, or Android device and open it in Safari or Chrome.
  - Add it to your Home Screen for a native app-like full-screen study experience that works seamlessly in airplane mode.
- **How to Deploy / Host Free:**
  - **GitHub Pages:** In repository **Settings > Pages**, set **Source** to *Deploy from a branch*, select branch `master` and folder `/web`.
  - **Local Static Server:** Run `python3 -m http.server 8000 -d web` and open `http://localhost:8000`.
  - **Static Cloud Hosts:** Connect the repo to Cloudflare Pages, Netlify, or Vercel and specify `web/` as the publish directory.
- **Key Features:**
  - **Timed 50-Question PSI Mock Exam:** 60-minute countdown timer, stratified blueprint quota sampling, question flag tracking, jump grid, and complete post-exam diagnostic review with domain breakdown.
  - **Domain Study Drill Mode:** Untimed practice filtered by any of the 6 official Georgia jurisprudence domains with immediate feedback and statutory citations.
  - **Missed Question Remediation:** Automatically remembers every question you miss using browser `localStorage` (100% private and persistent on your device).
  - **Accessibility & Themes:** Built-in Light and Dark modes, readable typography, and full keyboard navigation (`1`–`4` or `A`–`D`, `Next`, `Prev`, `Flag`).

---

### 📄 2. Printable & Tablet PDF Study Packets (`pdfs/`)

Typeset with professional CSS Paged Media standards for crisp printing or digital tablet markup (Apple Books, GoodNotes, Notability, Adobe Acrobat):

- **[Statutory Cheat Sheet PDF](pdfs/GAMB_Statutory_Cheat_Sheet.pdf)** (3 pages):
  - Ultra-high-yield synthesis of every statutory number, deadline, CE cap, and exception on the exam.
  - Highlights: 40 hrs CE (6 ethics, 3 psychopharmacology, 16 async max), 7-year adult record retention (7 yrs past age of majority for minors), 2-year post-termination sexual intimacy ban, mandatory child abuse reporting (§ 19-7-5: immediate oral report + 24-hr written report), elder abuse reporting (§ 30-5-4), and psychologist-patient privilege (§ 43-39-16).
- **[435-Question Compendium PDF](pdfs/GAMB_435_Question_Compendium.pdf)** (Comprehensive Worktext):
  - **Part I (Question Bank)**: All 435 curated questions organized by domain with multiple-choice stems. Questions contain **no spoilers or answers** on the page.
  - **Part II (Annotated Answer Key)**: Located in the back of the book, providing the correct option, primary statutory citation, and detailed legal rationale for every question.
- **Practice Exam Booklets ([Form A](pdfs/GAMB_Practice_Exam_Form_A.pdf), [Form B](pdfs/GAMB_Practice_Exam_Form_B.pdf), [Form C](pdfs/GAMB_Practice_Exam_Form_C.pdf))**:
  - Three distinct, non-overlapping 50-question mock exams generated with stratified blueprint quotas (14/13/9/6/5/3).
  - Each booklet includes:
    1. Official cover sheet with test administration instructions and 76% passing threshold.
    2. 50 exam questions without answers.
    3. Self-scoring bubble sheet grid for recording your responses.
    4. Back-of-book answer key and detailed legal rationales for self-grading.

---

### 🗂️ 3. Spaced-Repetition Anki Flashcards (`anki/gamb_deck.tsv`)

A curated deck of 435 atomic flashcards formatted for [Anki](https://apps.ankiweb.net/), [AnkiDroid](https://play.google.com/store/apps/details?id=com.ichi2.anki), and [AnkiMobile](https://apps.apple.com/us/app/ankimobile-flashcards/id373493387).

- **How to Import into Desktop Anki:**
  1. Open Anki (2.1+), select **File > Import...**
  2. Select [`anki/gamb_deck.tsv`](anki/gamb_deck.tsv).
  3. Set **Type** to `Basic` and target deck to `GA Jurisprudence GAMB`.
  4. Ensure field mapping is: Field 1 → `Front`, Field 2 → `Back`, Field 3 → `Tags`.
  5. Check "Allow HTML in fields" and click **Import**.
- **How to Study on Mobile:**
  - Sync your desktop Anki collection to your free [AnkiWeb](https://ankiweb.net) account.
  - Open **AnkiDroid** (Android) or **AnkiMobile** (iOS) and tap **Sync**.
  - Or study directly in any mobile web browser via [AnkiWeb](https://ankiweb.net).
- Full details and field mapping notes can be found in [`anki/README_import.md`](anki/README_import.md).

---

### 💻 4. Interactive Terminal Simulator (`gamb-exam`)

For candidates comfortable with Python and command-line environments who want a full-screen terminal user interface (TUI) matching PSI examination conditions.

```bash
# Clone the repository
git clone https://github.com/jbff/ga-psych-jurisprudence.git
cd ga-psych-jurisprudence

# Launch 60-minute timed 50-question PSI exam simulation
uv run gamb-exam test

# Launch untimed domain study drill (e.g. 20 questions on Licensure)
uv run gamb-exam study --domain licensure --count 20

# Drill questions previously answered incorrectly
uv run gamb-exam missed

# View historical performance diagnostics and pass/fail record
uv run gamb-exam stats

# Regenerate all study PDFs, docs, and web quizzer
uv run gamb-exam build-assets
```

---

## Overview & Exam Structure

The Georgia Jurisprudence Examination (GAMB) tests knowledge of Georgia statutory law (O.C.G.A.) and official Rules and Regulations of the State of Georgia (Department 510) governing the practice of psychology.

- **Format**: 50 scored multiple-choice questions (4 options each: A, B, C, D)
- **Time Limit**: 60 minutes
- **Condition**: Closed book, computer-based testing via PSI
- **Passing Cutoff**: **38 / 50 (76.0%)**

### Official 6-Domain Blueprint & Weighting

The examination follows the official Georgia Board blueprint across 6 core domains:

| Domain | Weight (%) | Questions | Content Summary |
| :--- | :---: | :---: | :--- |
| **Professional Relationships** | 28% | 14 | Multiple relationships, sexual intimacies (2-year rule), conflicts of interest, third-party requests, informed consent, supervisory duties |
| **Licensure and Regulations** | 26% | 13 | Qualifications, CE requirements (40 hrs/biennium), license renewal, Board disciplinary powers, scope of practice, unauthorized practice |
| **Competence** | 18% | 9 | Boundaries of competence, maintaining competence, impairment, bases for scientific judgments, delegating work |
| **Assessment** | 12% | 6 | Test selection, scoring, interpretation, automated reports, release of raw data vs. test stimuli, obsolete test materials |
| **Privacy and Confidentiality** | 10% | 5 | O.C.G.A. § 43-39-16 privileged communications, mandatory child abuse reporting (§ 19-7-5), elder abuse (§ 30-5-4), duty to protect |
| **Recordkeeping and Fees** | 6% | 3 | 7-year adult record retention, child retention (7 yrs past age of majority), fee arrangements, withholding records for nonpayment |
| **Total** | **100%** | **50** | |

---

## Interactive Terminal Exam Suite (`gamb-exam`)

The repository includes a modern, full-screen Terminal User Interface (TUI) and CLI application built with Python, [Textual](https://textual.textualize.io/), and [Rich](https://rich.readthedocs.io/). It simulates PSI examination conditions, tracks question flags, provides a visual jump grid, and generates granular diagnostic score reports.

### Quickstart

Install and run instantly with [uv](https://docs.astral.sh/uv/) (no manual virtual environment creation needed):

```bash
git clone https://github.com/jbff/ga-psych-jurisprudence.git
cd ga-psych-jurisprudence
uv run gamb-exam test
```

### Complete CLI Subcommands Reference

- **`uv run gamb-exam test`**  
  Launches the full 60-minute timed 50-question mock exam. Stratified sampling guarantees exact Board domain quotas (14/13/9/6/5/3) with randomized distractor order. Draws from a 100% curated 435-question bank where every multiple-choice option is a plausible Georgia legal foil. Features live countdown timer, flag tracking, navigation jump grid, and post-exam score diagnostics with domain-level breakdown and review mode.

- **`uv run gamb-exam study [--domain <domain>] [--count <N>]`**  
  Untimed study drill mode. Questions reveal immediate feedback, full statutory explanations, and legal citations upon answering.
  ```bash
  # Drill 20 questions from any domain
  uv run gamb-exam study --count 20

  # Drill specifically on Privacy and Confidentiality
  uv run gamb-exam study --domain privacy --count 10
  ```
  *(Supported domain filters: `prof-relationships`, `licensure`, `competence`, `assessment`, `privacy`, `recordkeeping`)*

- **`uv run gamb-exam missed`**  
  Targeted drill focusing exclusively on questions answered incorrectly in prior practice sessions. Perfect for focused remediation before exam day.

- **`uv run gamb-exam stats`**  
  Displays a rich diagnostic summary table of all completed practice exam sessions, scores, pass/fail status, and domain mastery percentages stored in your local session history.

- **`uv run gamb-exam export [--output mocks/]`**  
  Generates a fresh, balanced 50-question mock exam in printable/viewable Markdown format (`mock_questions.md`) alongside a complete annotated answer key (`mock_key.md`) with legal citations and explanations.

- **`uv run gamb-exam build-assets [--output .]`**  
  Compiles all consumer PDF study guides, practice exam booklets Form A/B/C, Markdown study packets, and the standalone offline Web Quizzer (`web/index.html`).

### Keyboard Navigation Reference

| Key | Action | Context |
| :--- | :--- | :--- |
| `[A]`, `[B]`, `[C]`, `[D]` (or `[1]`–`[4]`) | Select answer option | Exam & Study |
| `[N]` or `[Enter]` | Next question | Exam & Study |
| `[P]` | Previous question | Exam & Study |
| `[F]` | Flag / unflag current question for review | Exam |
| `[J]` | Toggle 5×10 question jump grid (shows answered, flagged, and unanswered items) | Exam |
| `[S]` | Submit exam (prompts confirmation with warning if unanswered questions remain) | Exam |
| `[Q]` | Quit application | Global |
| `[B]` or `[Esc]` | Return to diagnostic score report | Review Mode |
| `[R]` | Review all exam questions with citations & explanations | Post-Exam Results |
| `[M]` | Review missed questions only | Post-Exam Results |

---

## Study Corpus & Source Materials

The study corpus in `study_corpus/` represents the verified primary legal sources governing the practice of psychology in Georgia. Every document has been audited for statutory currency:

- **`study_corpus/STATUTES_OC_GA.md`**: Complete, unabridged primary text of all 44 Georgia Code sections on the Board reference list (Title 43 Ch. 39 Psychologists, Title 43 Ch. 1 General Provisions, Title 19 Ch. 7 Child Abuse Reporting, Title 30 Ch. 5 Disabled Adults, Title 31 Health, Title 37 Mental Health, Title 16 Crimes, Title 24 Evidence, Title 50 Open Records).
- **`study_corpus/RULES_510_FULL.md`**: Complete official text of the Rules and Regulations of the State of Georgia, Department 510 (State Board of Examiners of Psychologists), Chapters 510-1 through 510-10, including the complete Code of Conduct.
- **`study_corpus/EXAM_SYLLABUS_AND_TOPIC_MAPPING.md`**: Detailed mapping linking each of the 6 exam domains to statutory and administrative rule sections.
- **`MANIFEST.md`**: Full inventory and character/word counts of all source statutes.

---

## Curated Question Bank & Quality Guarantees

The full 435-question examination pool (`gamb_exam/question_pool.json`) has undergone a comprehensive, psychometric distractor audit and is officially versioned:
- **Versioned Pool Standard**: Labeled **Version 1.0 (Release Date: 10/25/2026)** with schema metadata in `gamb_exam/question_pool_metadata.json`. All generated PDF documents, markdown booklets, and the web application display this version in running headers and cover pages.
- **100% Context-Responsive Options**: Every distractor directly answers the question asked using plausible Georgia statutory numbers, procedures, or standards (no nonsense cross-domain fallback options).
- **Zero Test-Wiseness Flaws**: No bare "Yes" or "No" answers; all options are expanded into parallel explanatory clauses with uniform syntactic tone and balanced lengths.
- **Unambiguous Legal Accuracy**: Exactly one legally correct answer per question under O.C.G.A. Titles 43, 31, 37, 19, 30, 16, 24, 50, Georgia Board Rules (Chapter 510), and the APA Ethics Code.
- **Balanced Key Distribution**: Perfectly distributed answer keys across all 435 items (~25% each across A, B, C, and D).
- **Stateless Database Generation**: The SQLite database (`data/gamb_exam.db`) is generated on-demand at runtime from `gamb_exam/question_pool.json` and kept strictly outside git tracking.

---

## Development & Verification

### Prerequisites
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

### Running the Test Suite
```bash
# Run pytest with uv
uv run pytest
```
All 72 unit, pool, CLI, TUI, and asset build tests verify:
- SQLite question pool integrity, unique IDs 1–435, schema conformity, distractor uniqueness, and citation validity (`test_question_pool.py`, `test_seed.py`, `test_db.py`).
- Stratified 50-question mock exam sampler and Markdown export formatting (`test_generator.py`).
- TUI state machines, navigation, flag toggling, answer scoring, timer operations, and review mode (`test_tui.py`).
- CLI argument parsing, help output, and subcommands (`test_cli.py`).
- PDF stylesheet compilation, HTML generation, Markdown export, and single-file web quizzer bundling (`test_build_assets.py`).
