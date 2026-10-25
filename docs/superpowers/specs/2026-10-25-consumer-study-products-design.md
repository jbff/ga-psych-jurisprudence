# Design Specification: Consumer-Friendly Study Products & Assets

**Date:** 2026-10-25  
**Status:** Approved  
**Target Repository:** `jbff/ga-psych-jurisprudence` (`gamb-exam`)  
**Scope:** Automated generation and packaging of consumer-ready study products (PDF documents, offline web quizzer, cheat sheet, and repository documentation) requiring zero terminal or Python setup.

---

## 1. Executive Summary & Goals

The Georgia Psychology Jurisprudence Examination study suite contains a verified, 435-question curated pool and terminal exam simulator. However, most licensing candidates cannot or will not install Python, run terminal commands, or use a command-line interface.

This specification defines the architecture, data pipeline, and delivery formats for a consumer-focused distribution tier:
1. **Zero-Install Offline Web Quizzer (`web/index.html`)**: A standalone, single-file HTML5/CSS/JS application embedding all 435 questions, providing 50-question timed mock exams, domain-by-domain study drilling, and missed-question remediation. Operable locally in any browser on desktop or mobile, or deployable to a personal website (`johnbflemingphd.com`).
2. **Printable Document Suite (`pdfs/`)**:
   - `GAMB_Statutory_Cheat_Sheet.pdf`: High-yield 2–3 page quick-reference guide of statutory numbers, timeframes, penalties, and exceptions.
   - `GAMB_435_Question_Compendium.pdf`: Complete 435-question worktext divided into Part I (Questions by Domain) and Part II (Annotated Answer Key & Citations in the back).
   - `GAMB_Practice_Exam_Form_A.pdf`, `Form_B.pdf`, `Form_C.pdf`: Three distinct 50-question mock exams matching official Board domain quotas (14/13/9/6/5/3) with cover instructions, bubble answer sheets, and answer keys in the back.
3. **Automated Pipeline (`gamb_exam/build_assets.py`)**: A deterministic compiler that ingests `gamb_exam/question_pool.json`, renders semantic HTML/CSS print stylesheets, and compiles vector PDFs via WeasyPrint.
4. **Prominent README Presentation**: A dedicated top-level section in `README.md` highlighting all consumer products with direct download links and clear usage guides.

---

## 2. Directory Layout & Distribution Endpoints

```
ga-psych-jurisprudence/
├── gamb_exam/
│   ├── question_pool.json           # Single source of truth (435 curated items)
│   ├── build_assets.py              # Exporter for PDFs, HTML compendiums, and Web Quizzer
│   └── cli.py                       # CLI command: 'gamb-exam build-assets'
├── pdfs/                            # Committed, publication-ready PDF downloads
│   ├── GAMB_Statutory_Cheat_Sheet.pdf
│   ├── GAMB_435_Question_Compendium.pdf
│   ├── GAMB_Practice_Exam_Form_A.pdf
│   ├── GAMB_Practice_Exam_Form_B.pdf
│   └── GAMB_Practice_Exam_Form_C.pdf
├── docs/
│   └── study_materials/             # Raw Markdown & HTML sources for online reading
│       ├── cheat_sheet.md
│       ├── compendium_questions.md
│       ├── compendium_key.md
│       ├── practice_exam_form_a.md
│       ├── practice_exam_form_b.md
│       └── practice_exam_form_c.md
├── web/
│   └── index.html                   # Zero-install standalone Web Quizzer (HTML + CSS + JS)
├── anki/
│   ├── gamb_deck.tsv                # 435-card flashcard deck for mobile spaced repetition
│   └── README_import.md
├── tests/
│   └── test_build_assets.py         # Automated pipeline & asset integrity test suite
└── README.md                        # Updated consumer-first documentation
```

---

## 3. Product Specifications

### 3.1 Statutory Quick-Reference Cheat Sheet (`GAMB_Statutory_Cheat_Sheet.pdf`)
A dense, 2–3 page quick-reference table designed for final-week review:
- **Licensing & Continuing Education**:
  - 40 CE hours per biennium (ending Dec 31 of even years).
  - 6 hours in Professional Ethics.
  - Area I (minimum 20 hrs, no maximum) vs. Area II (maximum 16 hrs total, individual caps).
  - Academic courses (10 hrs/course, max 20).
  - First/second author peer-reviewed publication: 10 hrs.
  - Pre-doc internship: 1,500 hrs; Post-doc SWE: 1,500 hrs (or 2,000 hrs if prior to deg conferral).
  - Maximum 3 concurrent supervisees without prior Board approval.
- **Mandatory Reporting Overrides**:
  - Child Abuse (O.C.G.A. § 19-7-5): Immediate, not later than 24 hours to DFCS or law enforcement. Psychologist-client privilege abrogated. Misdemeanor for failure to report. Good-faith immunity.
  - Elder / Disabled Adult Abuse (O.C.G.A. § 30-5-4): Report to Adult Protective Services (DHS) or law enforcement immediately. Privilege abrogated. Law enforcement must forward within 24 hours.
- **Privilege & Evidence**:
  - O.C.G.A. § 43-39-16 / § 24-5-501: Psychologist-client communications on same basis as attorney-client.
  - Form 1013 Emergency Involuntary Examination (§ 37-3-41): Psychologist authorized to execute; peace officer must take custody within 72 hours.
- **Criminal Penalties & Disciplinary Caps**:
  - Psychotherapist Sexual Misconduct (O.C.G.A. § 16-6-5.1): 1st degree felony (1–25 years, up to $100k fine); 2nd degree high & aggravated misdemeanor. Client consent is legally no defense.
  - Board Disciplinary Fines (O.C.G.A. § 43-1-19): Up to $500.00 civil fine per violation.
  - Unlicensed Practice (O.C.G.A. § 43-39-17): Misdemeanor, $100–$1,000 fine and/or up to 12 months imprisonment.
- **Recordkeeping & Out-of-State Practice**:
  - Adult records: Retain minimum 7 years.
  - Minor records: Retain 7 years past age of majority (age 25).
  - Emergency records: Cannot be withheld solely for nonpayment (APA 6.03).
  - Out-of-state practice (§ 43-39-7(8)): Max 30 days per calendar year with Board notice/approval; PSYPACT unlimited telepsychology / 30-day temporary in-person.

### 3.2 435-Question Domain Compendium (`GAMB_435_Question_Compendium.pdf`)
A comprehensive self-study workbook:
- **Part I: Question Bank by Domain**:
  - All 435 questions arranged under the 6 Board domains:
    1. Professional Relationships (73 questions)
    2. Licensure and Regulations (185 questions)
    3. Competence (104 questions)
    4. Assessment (30 questions)
    5. Privacy and Confidentiality (22 questions)
    6. Recordkeeping and Fees (21 questions)
  - Questions display stem and options A, B, C, D without marked answers.
- **Part II: Annotated Answer Key & Statutory Citations**:
  - Positioned at the back of the compendium.
  - Tabulated by Question ID (1–435), indicating:
    - Domain
    - Correct Option Letter (A, B, C, D)
    - Primary Legal Citation (O.C.G.A. section or Board Rule number)
    - Complete explanatory rationale

### 3.3 Practice Exam Booklets (Forms A, B, and C)
Three complete 50-question mock exams:
- Sourced deterministically from `gamb_exam/question_pool.json` using fixed seeds:
  - Form A: Seed 101
  - Form B: Seed 202
  - Form C: Seed 303
- Exact Board domain quotas guaranteed:
  - Professional Relationships: 14 items
  - Licensure and Regulations: 13 items
  - Competence: 9 items
  - Assessment: 6 items
  - Privacy and Confidentiality: 5 items
  - Recordkeeping and Fees: 3 items
- Content Layout:
  - Cover page with official instructions, 60-minute time limit, 38/50 (76%) passing score rule, and disclaimers.
  - 50 questions (unmarked).
  - Printable bubble sheet / self-scoring table.
  - Annotated answer key and statutory notes at the back.

### 3.4 Zero-Install Offline Web Quizzer (`web/index.html`)
A standalone single-file web application:
- **Zero External Dependencies**: All HTML, CSS, JavaScript, and the complete 435-question JSON bank are inlined in one file.
- **Portability**: Opens directly via `file://` protocol in any web browser without a local web server or internet connection.
- **Modes**:
  1. **PSI Simulation Exam**: Timed 60-minute, 50-question exam with exact domain quotas, countdown timer, question flagging (`[F]`), 5x10 navigation grid, instant scoring against the 76% threshold, and domain breakdown.
  2. **Domain Study Drill**: Practice questions by selected domain with immediate feedback (green/red styling, citation, and explanation on answer click).
  3. **Missed Questions Drill**: Retest questions missed in previous sessions (persisted via browser `localStorage`).
- **Responsive Design**: Full mobile support (phones/tablets) and desktop keyboard navigation (`A`/`B`/`C`/`D`, `Enter`, `N`, `P`, `F`).

---

## 4. Build Pipeline Architecture & Implementation

### 4.1 CLI Subcommand
Extend `gamb_exam/cli.py` with:
```bash
uv run gamb-exam build-assets [--output-dir <path>]
```
Default output paths:
- PDF files -> `pdfs/`
- Markdown sources -> `docs/study_materials/`
- Web Quizzer -> `web/index.html`

### 4.2 PDF Generation Engine
- **HTML + CSS Paged Media**:
  - Semantic HTML templates using `@page` rules for standard US Letter size (`size: letter; margin: 0.75in;`).
  - Running headers (`"Georgia Psychology Jurisprudence Examination Study Guide"`) and dynamic footers with page counters (`content: "Page " counter(page) " of " counter(pages);`).
  - Rule `page-break-inside: avoid;` on all question blocks to prevent awkward question splits across page breaks.
- **Compiler**:
  - Python calls `weasyprint.HTML(string=...).write_pdf(output_path)` (or fallback shell wrapper to `/usr/bin/weasyprint`).

---

## 5. Testing & Quality Assurance

### 5.1 Test Suite (`tests/test_build_assets.py`)
1. **Pipeline Execution**: Verifies `build_assets()` runs successfully without error.
2. **File Existence & Integrity**:
   - Asserts all 5 PDF files exist in `pdfs/` and have non-zero file sizes (>10KB).
   - Asserts `web/index.html` exists and contains valid HTML structure with all 435 questions embedded.
3. **Practice Form Quotas**:
   - Asserts Forms A, B, and C each draw exactly 50 items matching the exact domain quotas (14, 13, 9, 6, 5, 3).
   - Asserts Forms A, B, and C have distinct question selections.
4. **HTML Escaping & Content Integrity**:
   - Verifies all statutory quotes, ampersands, and angle brackets are properly escaped in the generated HTML and Markdown files.

---

## 6. Documentation & README Integration

Update `README.md` to feature a top-level **"📦 Study Products & Downloads (No Installation Required)"** section immediately following the disclaimer:
- Overview table of all study formats.
- Direct file links to each PDF in `pdfs/`.
- Clear instructions on how to use `web/index.html` on desktop and mobile.
- Guide on importing `anki/gamb_deck.tsv` into AnkiWeb / AnkiDroid / AnkiMobile.
