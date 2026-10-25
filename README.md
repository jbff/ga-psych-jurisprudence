# Georgia Psychology Jurisprudence Examination (GAMB) Study Kit & Simulator

> [!WARNING]
> **LEGAL & REGULATORY DISCLAIMER**:
> The study materials, question pools, flashcards, and practice exams contained in this repository are **independently generated study aids** and are **NOT official examination questions** from the Georgia State Board of Examiners of Psychologists, PSI Services LLC, or the Association of State and Provincial Psychology Boards (ASPPB). No guarantee, warranty, or representation is made regarding the accuracy, completeness, timeliness, or utility of these materials, or that studying them will result in a passing score on the Georgia Jurisprudence Examination (GAMB). Use of these materials is entirely at your own risk. The authors and contributors disclaim all liability for any claims, damages, direct or consequential losses, or examination failures arising from the use of or reliance upon these materials.

---

A comprehensive, rigorously audited jurisprudence examination study kit and interactive terminal exam simulator for psychologists preparing for the **Georgia Jurisprudence Examination (GAMB)** administered via PSI Services.

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

## Anki Flashcard Deck

Located at `anki/gamb_deck.tsv` (with import guide in `anki/README_import.md`):

- **435 Spaced-Repetition Cards**: 100% substantive Georgia statutory law and Board rules.
- **Zero Administrative Fluff**: Purged of testing center parking policies, dress codes, exam fees, and obsolete logistics.
- **Atomic, Tested Facts**: Every card tests a discrete statutory rule or legal threshold, complete with an exact legal citation (e.g., `O.C.G.A. § 43-39-7`, `Rule 510-5-.04`).
- **Domain Tagging**: Cleanly tagged by the 6 examination domains:
  - `licensure` (185 cards)
  - `competence` (104 cards)
  - `prof-relationships` (73 cards)
  - `assessment` (30 cards)
  - `privacy` (22 cards)
  - `recordkeeping` (21 cards)

### How to Import

1. **Desktop Anki**:
   - Open Anki (2.1+), select **File > Import...**
   - Choose `anki/gamb_deck.tsv`.
   - Set **Note Type** to `Basic` and target deck to `GA Jurisprudence GAMB`.
   - Ensure fields are mapped to `Front`, `Back`, and `Tags`.
2. **Mobile (iOS & Android)**:
   - Sync your desktop deck via a free [AnkiWeb](https://ankiweb.net) account.
   - Study on mobile via **AnkiDroid** (Android, 100% free open-source) or **AnkiMobile** (iOS), or use **AnkiWeb directly in any mobile web browser** for completely free cross-platform mobile access.

---

## Study Corpus & Source Materials

The study corpus in `study_corpus/` represents the verified primary legal sources governing the practice of psychology in Georgia. Every document has been audited for statutory currency:

- **`study_corpus/STATUTES_OC_GA.md`**: Complete, unabridged primary text of all 44 Georgia Code sections on the Board reference list (Title 43 Ch. 39 Psychologists, Title 43 Ch. 1 General Provisions, Title 19 Ch. 7 Child Abuse Reporting, Title 30 Ch. 5 Disabled Adults, Title 31 Health, Title 37 Mental Health, Title 16 Crimes, Title 24 Evidence, Title 50 Open Records).
- **`study_corpus/RULES_510_FULL.md`**: Complete official text of the Rules and Regulations of the State of Georgia, Department 510 (State Board of Examiners of Psychologists), Chapters 510-1 through 510-10, including the complete Code of Conduct.
- **`study_corpus/EXAM_SYLLABUS_AND_TOPIC_MAPPING.md`**: Detailed mapping linking each of the 6 exam domains to statutory and administrative rule sections.
- **`MANIFEST.md`**: Full inventory and character/word counts of all source statutes.

---

## Curated Question Bank & Quality Guarantees

The full 435-question examination pool (`gamb_exam/question_pool.json`) has undergone a comprehensive, psychometric distractor audit:
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
All 54 unit, pool, and integration tests verify:
- SQLite question pool integrity, unique IDs 1–435, schema conformity, distractor uniqueness, and citation validity (`test_question_pool.py`, `test_seed.py`, `test_db.py`).
- Stratified 50-question mock exam sampler and Markdown export formatting (`test_generator.py`).
- TUI state machines, navigation, flag toggling, answer scoring, timer operations, and review mode (`test_tui.py`).
- CLI argument parsing, help output, and subcommands (`test_cli.py`).
