# Georgia Psychology Jurisprudence Examination (GAMB) Study Kit & Simulator

> [!WARNING]
> **LEGAL & REGULATORY DISCLAIMER & EXAM REALITY NOTICE**:
> The study materials, question pools, flashcards, reference sheets, and practice exams contained in this repository are **independently authored study aids** and are **NOT official examination materials** from the Georgia State Board of Examiners of Psychologists, PSI Services LLC, or the Association of State and Provincial Psychology Boards (ASPPB). While based on public statutory and regulatory texts (O.C.G.A. and Georgia Board Rules Chapter 510), these materials **have not been verified, reviewed, or approved by any licensing board, testing vendor, or regulatory authority**.
>
> **Field Validation & Exam Format Reality**: In an *n*=1 sample, the author passed the actual Georgia Psychology Jurisprudence Examination (GAMB) administered at PSI after studying solely from Version 1.0 of this question pool and flashcard deck. The repository has since been expanded in Version 2.0 (11/06/2026) to be even more thorough. **However, candidates must be aware that the format, details, narrative structure, complexity, and approach of the questions on the actual GAMB exam are NOT AT ALL like the direct, fact-checking practice questions in this package.** The actual examination heavily features applied clinical vignettes, practical decision-making, and indirect scenarios. While it has been our deliberate **aim to cover all testable legal and regulatory facts** so that candidates have the raw statutory knowledge necessary to reason through complex questions on the real exam, **we make no claim, representation, or guarantee that all testable facts are covered**, or that studying this material will result in a passing score. Laws and regulations change, and these materials may contain errors or omissions. Use of these materials is entirely at your own risk. The author and contributors disclaim all liability for any claims, damages, direct or consequential losses, examination outcomes, or reliance upon these materials.

---

A structured, independently developed jurisprudence examination study kit, printable PDF library, zero-install offline web quizzer, and interactive terminal simulator designed to assist psychologists preparing for the **Georgia Jurisprudence Examination (GAMB)** administered via PSI Services.

> [!IMPORTANT]
> **Noncommercial License & Terms of Use**:
> The study materials, question pool, and software provided in this repository are licensed under the **[PolyForm Noncommercial License 1.0.0](LICENSE.md)**.
> - **Personal Noncommercial Study**: Licensure candidates and students may read, run, and study these materials for personal examination preparation.
> - **Commercial Exploitation Prohibited**: Third parties may not sell, paywall, monetize, bundle, or use any part of these materials (PDFs, questions, software, or web tools) for commercial courses, paid prep services, or resale.
> - **Commercial Rights Reserved**: All commercial exploitation rights are exclusively reserved by author [John B. Fleming, PhD](http://johnbflemingphd.com), who reserves the right to package, sell, or offer compiled study products, online simulators, or future versions under separate commercial terms.

---

## 📦 Study Products & Downloads (No Installation Required)

The study aids provided in this repository are packaged in ready-to-use, zero-dependency consumer formats to support candidate preparation. You do **not** need programming knowledge, Python, or command-line tools to start studying immediately. All study products are compiled from **Question Pool Version 2.0 (Release Date: 11/06/2026)** and structured around our **205-item Atomic Fact Inventory** (`data/fact_inventory.json`).

> 💡 **Pre-Packaged Downloads Available**: You can download individual PDFs, the offline web quizzer, Anki flashcards, or the all-in-one ZIP archive (`GAMB_Study_Package_v2.0_All_Files.zip`) directly from the **[GitHub v2.0 Release](https://github.com/jbff/ga-psych-jurisprudence/releases/tag/v2.0)**.

### 📚 Downloadable Study Packets & Flashcards

| Product | Format | Description | Direct Access / Link |
| :--- | :---: | :--- | :--- |
| **Numbers & Deadlines Cram Sheet** | `PDF` | Chronological fast-lookup tables compiling statutory hours, days, months, years, and supervision ratios identified in the study corpus. | [Download Numbers Cheat Sheet PDF](pdfs/GAMB_Numbers_And_Deadlines_Cheat_Sheet.pdf) |
| **Statutory Cheat Sheet** | `PDF` | Thematic deep-dive cross-referencing O.C.G.A. Titles 16, 19, 30, 37, 43, 50 and Board Rules Chapter 510. | [Download Statutory Cheat Sheet PDF](pdfs/GAMB_Statutory_Cheat_Sheet.pdf) |
| **472-Question Compendium** | `PDF` | Self-study question compendium organized by domain (Part I: Questions without answers; Part II: Back-of-book annotated key & citations). | [Download Compendium PDF](pdfs/GAMB_Question_Compendium.pdf) |
| **Practice Exam Form A** | `PDF` | 50-question mock exam booklet with instructions, bubble sheet, and annotated answer key in back. | [Download Form A PDF](pdfs/GAMB_Practice_Exam_Form_A.pdf) |
| **Practice Exam Form B** | `PDF` | 50-question mock exam booklet with instructions, bubble sheet, and annotated answer key in back. | [Download Form B PDF](pdfs/GAMB_Practice_Exam_Form_B.pdf) |
| **Practice Exam Form C** | `PDF` | 50-question mock exam booklet with instructions, bubble sheet, and annotated answer key in back. | [Download Form C PDF](pdfs/GAMB_Practice_Exam_Form_C.pdf) |
| **Anki Flashcard Deck** | `TSV` | 472 atomic flashcards for Anki, AnkiDroid, and AnkiMobile. | [anki/gamb_deck.tsv](anki/gamb_deck.tsv) |

*(Note: Raw Markdown versions of all study guides and exam forms are also available in [`docs/study_materials/`](docs/study_materials/).)*

### 💻 Interactive Test Engines & Simulators

| Product | Format | Description | Direct Access / Run Command |
| :--- | :---: | :--- | :--- |
| **Interactive Web Quizzer** | `index.html` | Timed 50-q PSI exam simulator, domain study drill, and missed question review. Runs 100% offline in any browser. | [web/index.html](web/index.html) |
| **Terminal Simulator (CLI/TUI)** | `Python` | Full-screen terminal exam simulation with live countdown timer, flag tracking, jump grid, and score diagnostics. | `uv run gamb-exam test` |

---

### 📄 1. Printable & Tablet PDF Study Packets (`pdfs/`)

Typeset with professional CSS Paged Media standards for crisp printing or digital tablet markup (Apple Books, GoodNotes, Notability, Adobe Acrobat):

- **[Numbers & Deadlines Cram Sheet PDF](pdfs/GAMB_Numbers_And_Deadlines_Cheat_Sheet.pdf)** (and [Markdown](docs/study_materials/numbers_cheat_sheet.md)):
  - Fast-lookup chronological cram sheet designed specifically for memorizing numerical test items.
  - Compiles key statutory timeframes identified in the rules and code into four tables: **The Clock (Hours)** for emergency commitments and mandatory reporting; **The Calendar (Days)** for application deadlines, temporary practice limits, conviction notices, and late renewal grace periods; **Months & Years** for training completion windows, license durations, and record retention; and **Supervision & Standards** for supervision ratios, CE caps, and passing cutoffs.
- **[Statutory Cheat Sheet PDF](pdfs/GAMB_Statutory_Cheat_Sheet.pdf)** (and [Markdown](docs/study_materials/cheat_sheet.md)):
  - Thematic quick-reference summary cross-referencing Georgia Code and Board rules across 4 core domains: *Licensure, Supervision & Continuing Education*; *Mandatory Reporting & Emergency Involuntary Commitment*; *Confidentiality, Evidentiary Privilege & Prohibited Relationships*; and *Recordkeeping, Practice Limits & Disciplinary Penalties*.
- **[472-Question Compendium PDF](pdfs/GAMB_Question_Compendium.pdf)** (Question Compendium):
  - **Part I (Question Bank)**: All 472 curated questions organized by domain with multiple-choice stems. Questions contain **no spoilers or answers** on the page.
  - **Part II (Annotated Answer Key)**: Located in the back of the book, providing the correct option, primary statutory citation, and detailed legal rationale for every question.
- **Practice Exam Booklets ([Form A](pdfs/GAMB_Practice_Exam_Form_A.pdf), [Form B](pdfs/GAMB_Practice_Exam_Form_B.pdf), [Form C](pdfs/GAMB_Practice_Exam_Form_C.pdf))**:
  - Three distinct, non-overlapping 50-question mock exams generated with stratified blueprint quotas (14/13/9/6/5/3).
  - Each booklet includes:
    1. Official cover sheet with test administration instructions and 76% passing threshold.
    2. 50 exam questions without answers.
    3. Self-scoring bubble sheet grid for recording your responses.
    4. Back-of-book answer key and detailed legal rationales for self-grading.

---

### 🗂️ 2. Spaced-Repetition Anki Flashcards (`anki/gamb_deck.tsv`)

A curated deck of 472 atomic flashcards formatted for [Anki](https://apps.ankiweb.net/), [AnkiDroid](https://play.google.com/store/apps/details?id=com.ichi2.anki), and [AnkiMobile](https://apps.apple.com/us/app/ankimobile-flashcards/id373493387).

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

### 🌐 3. Interactive Web Quizzer (`web/index.html`)

A standalone, self-contained single-file web application with all 472 questions, distractors, legal rationales, and statutory citations embedded directly in the file. It runs completely offline with zero installation or external network requests.

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

# View cumulative per-item study progress by domain
uv run gamb-exam progress --missed

# Regenerate all study PDFs, docs, and web quizzer
uv run gamb-exam build-assets
```

---

## Overview & Exam Structure

The Georgia Jurisprudence Examination (GAMB) tests knowledge of Georgia statutory law (O.C.G.A.) and official Rules and Regulations of the State of Georgia (Department 510) governing the practice of psychology.

- **Exam Delivery**: Computer-based testing administered at PSI testing centers (or approved remote proctoring)
- **Format**: **60 multiple-choice questions** presented in 60 minutes (4 options each: A, B, C, D)
  - **50 Scored Items**: Sampled strictly according to the official 6-domain Board blueprint below
  - **Up to 10 Unscored Pretest Items**: As documented in PSI Candidate Information Bulletin #1755, the testing vendor includes unscored experimental questions to evaluate items for future forms; these do not count toward your score
- **Time Limit**: 60 minutes (averaging 60 seconds per item across all 60 questions)
- **Condition**: Closed book, computer-based testing via PSI
- **Passing Cutoff**: **38 / 50 scored items (76.0%)**

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
  Launches a 60-minute timed 50-question mock exam. Stratified sampling applies Board domain blueprint proportions (14/13/9/6/5/3) with randomized distractor order. Draws from a curated 472-question bank where distractors are drafted to reflect plausible Georgia legal standards and statutory numbers. Features live countdown timer, flag tracking, navigation jump grid, and post-exam score diagnostics with domain-level breakdown and review mode.

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

- **`uv run gamb-exam progress [--missed]`**  
  Cumulative per-item study statistics across all practice sessions. Shows how many distinct questions you have seen in each domain, how many you have never answered wrong ("clean"), and how many you have ever answered wrong. The `--missed` flag also lists questions whose most recent answered attempt was wrong.

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

The study corpus in `study_corpus/` and modular source repository in `sources/` provide reference copies of key Georgia statutes, administrative rules, and incorporated authorities relevant to the examination syllabus:

- **`study_corpus/STATUTES_OC_GA.md`**: Reference text of **48 Georgia Code sections** compiled for examination study—including the 44 sections from the Board's published reference list alongside 4 key 1-hop incorporated satellite statutes added in Version 2.0:
  - **Title 43 Ch. 39**: Georgia Psychology Practice Act (O.C.G.A. §§ 43-39-1 through 43-39-20).
  - **Title 43 Ch. 1**: General Provisions for Professional Licensing Boards (§§ 43-1-19 through 43-1-25, and § 43-1-27 felony notification).
  - **Title 19 Ch. 7**: Mandatory Child Abuse Reporting (§ 19-7-5, with 2025 recodification notes).
  - **Title 16 Ch. 6**: Sexual Offenses incorporated into child abuse reporting and psychotherapist misconduct:
    - **§ 16-6-3**: Statutory rape (elements, victim < 16, and close-in-age Romeo & Juliet misdemeanor exceptions).
    - **§ 16-6-4**: Child molestation & aggravated child molestation (elements, digital transmission, physical injury/sodomy aggravating factors, and close-in-age misdemeanor exceptions).
    - **§ 16-6-5**: Enticing a child for indecent purposes (luring/asportation elements and close-in-age misdemeanor exceptions).
    - **§ 16-6-5.1**: Sexual assault by persons with supervisory authority / psychotherapists.
  - **Title 24 Evidence**: Privileged communications:
    - **§ 24-5-501**: Privileged communications under the post-2013 Evidence Code, anchoring psychologist-patient privilege to attorney-client standards and creating multidisciplinary psychotherapy team privilege.
    - **§ 24-9-21**: Predecessor privilege statute referenced in historical board materials.
  - **Title 30 Ch. 5**: Protection of Disabled Adults and Elder Persons (§ 30-5-4 reporting mandate).
  - **Title 31 Ch. 7**: Health Service Provider Psychologists and hospital staff privileges (§§ 31-7-160 through 31-7-165).
  - **Title 37 Ch. 3**: Examination, Treatment, and Involuntary Patients (§ 37-3-41 Form 1013 emergency admission authority).
  - **Title 16 Ch. 13**: Controlled Substances license sanctions (§§ 16-13-110 through 16-13-114).
  - **Title 50 Ch. 13 & 18**: Georgia Administrative Procedure Act and Open Records Act provisions referenced in board hearings and child abuse record confidentiality.
- **`study_corpus/RULES_510_FULL.md`**: Official reference text of the Rules and Regulations of the State of Georgia, Department 510 (State Board of Examiners of Psychologists), Chapters 510-1 through 510-10, including Chapter 510-4 (APA Ethics Code) and Chapter 510-5 (Supplemental Code of Conduct).
- **`study_corpus/EXAM_SYLLABUS_AND_TOPIC_MAPPING.md`**: Detailed mapping linking each of the 6 exam domains to statutory and administrative rule sections.
- **`data/fact_inventory.json`**: Structured inventory of **205 atomic legal and regulatory facts** identified from primary sources during our curriculum review, each mapped with statutory citations, machine domain slugs, question IDs, and Anki card tags.
- **`sources/`**: Modular directory preserving individual statute files (`sources/ocga_43-39/`, `sources/ocga_satellites/`), Department 510 official rules, and PSI Candidate Bulletin #1755.
- **`MANIFEST.md`**: Full audit manifest, line/word counts, and verification status for all primary source files.

---

## Curated Question Bank & Design Standards

The full 472-question examination pool (`gamb_exam/question_pool.json`) has undergone structured editorial review and is officially versioned:
- **Versioned Pool Standard**: Labeled **Version 2.0 (Release Date: 11/06/2026)** with schema metadata in `gamb_exam/question_pool_metadata.json`. All generated PDF documents, markdown booklets, and the web application display this version in running headers and cover pages.
- **Targeted Atomic Fact Alignment**: Each question in the pool is designed to align directly with an identified atomic fact in `data/fact_inventory.json` with bidirectional traceability across questions and flashcards.
- **Distractor Review & Balanced Alternatives**: Polar questions have been reviewed and structured to avoid obvious giveaway distractors (avoiding 3-Yes/1-No or 1-Yes/3-No imbalances; utilizing balanced 2-Yes/2-No formulations with distinct legal rationales or declarative non-polar choices).
- **Context-Responsive Options**: Distractors are drafted to address the question prompt directly using plausible Georgia statutory numbers, procedures, or standards, avoiding arbitrary or non-contextual fallback choices.
- **Syntax and Distractor Balance**: Avoids bare "Yes" or "No" answers; options are written with parallel explanatory clauses, uniform syntactic tone, and comparable lengths.
- **Grounded Legal Rationale**: Each question is keyed to a specific statutory citation or administrative rule under O.C.G.A., Georgia Board Rules (Chapter 510), or the APA Ethics Code, with an intended single best answer supported by legal rationale.
- **Balanced Key Distribution**: Answer keys are roughly evenly distributed across all 472 items (~25% each across A, B, C, and D) to prevent position bias.
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
All **103 unit, pool, CLI, TUI, fact inventory, and asset build tests** verify:
- Fact inventory integrity, verifying that all 205 inventory items map to questions and flashcards in the repository with valid statutory citations and schema conformity (`test_fact_inventory.py`).
- SQLite question pool integrity, unique IDs 1–472, schema conformity, distractor uniqueness, and polar giveaway prevention (`test_question_pool.py`, `test_seed.py`, `test_db.py`).
- Stratified 50-question mock exam sampler and Markdown export formatting (`test_generator.py`).
- TUI state machines, navigation, flag toggling, answer scoring, timer operations, and review mode (`test_tui.py`).
- CLI argument parsing, help output, and subcommands (`test_cli.py`).
- PDF stylesheet compilation, HTML generation, Markdown export, and single-file web quizzer bundling (`test_build_assets.py`).

---

## Author & Copyright

&copy; 2026 [John B. Fleming, PhD](http://johnbflemingphd.com). All rights reserved.

---

## License & Terms of Use

This repository and its contents are licensed under the **[PolyForm Noncommercial License 1.0.0](LICENSE.md)**.

- **Noncommercial Use Only**: Candidates, students, and educators may study and run these repository materials for personal, noncommercial examination preparation.
- **Commercial Rights Reserved**: All commercial rights—including the right to sell compiled PDF packages, printed materials, question bank licenses, paid courses, or monetized online test simulators—are strictly and exclusively reserved by John B. Fleming, PhD.
- **Right to Commercialize or Withhold Future Products**: The author reserves the right to package, sell, or offer future versions, compiled artifacts, or interactive platforms under separate commercial terms.


