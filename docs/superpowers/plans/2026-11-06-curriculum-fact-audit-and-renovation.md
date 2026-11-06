# Curriculum Fact Audit, Primary Source Re-Verification & Question Bank Renovation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Execute a comprehensive, ground-up audit of the Georgia Psychology Jurisprudence curriculum: independently verify and update all primary sources (including 1-hop incorporated criminal definitions for child sexual abuse), extract an exhaustive atomic fact inventory, repair unbalanced binary distractors across the question pool, and synchronize newly generated items into Anki and practice exam assets to achieve 100% fact coverage.

**Architecture:** A centralized, machine-validated atomic fact inventory (`data/fact_inventory.json`) acts as the single source of truth for all testable statutory and administrative requirements. Question pool items (`gamb_exam/question_pool.json`) and Anki flashcards (`anki/gamb_deck.tsv`) are linked via fact IDs and maintained in strict 1:1 parity, auto-seeding the SQLite exam database (`data/gamb_exam.db`) and derived study assets.

**Tech Stack:** Python 3.12+, `pytest`, `sqlite3`, `uv`, standard library JSON/TSV processing, Markdown.

**Spec:** [`docs/superpowers/specs/2026-11-06-curriculum-fact-audit-and-renovation-design.md`](file:///sto/hom/prj/ga-psych-jurisprudence/docs/superpowers/specs/2026-11-06-curriculum-fact-audit-and-renovation-design.md)

## Global Constraints

- **Single Correct Answer**: Every question must have exactly one unambiguously correct answer under Georgia law.
- **Distractor Balance**: No binary question may contain 3 Yes / 1 No or 3 No / 1 Yes options; all polar questions must feature either balanced 2-Yes / 2-No options with distinct legal rationales or premise-based declarative options without "Yes/No" cues.
- **1-Hop Incorporation Boundary**: External criminal code sections cited within primary syllabus statutes (e.g., O.C.G.A. § 19-7-5 citing § 16-6-3 statutory rape, § 16-6-4 child molestation, and § 16-6-5 enticing a child) are imported for their core substantive definitions, elements, and age thresholds, strictly stopping at 1 hop.
- **Backwards Compatibility**: Codebase domain slugs (`licensure`, `privacy`, `prof-relationships`, `competence`, `assessment`, `recordkeeping`) must be preserved in all data files to prevent regressions in exam generators and test suites.
- **1:1 Parity**: `question_pool.json` IDs (1 to $N$) must correspond exactly 1:1 with line numbers in `anki/gamb_deck.tsv`.

## Review Focus

1. **Binary Distractor Giveaways**: Any polar question where three choices share one polarity and the fourth choice is the opposite, allowing the answer to be deduced without reading the reasoning.
2. **Missing Statutory Age/Relationship Brackets**: Child sexual abuse reporting questions failing to specify the precise age thresholds under O.C.G.A. § 16-6-3 (< 16 years, perpetrator >= 18 vs 16-18 Romeo & Juliet exemption) or § 16-6-4 (< 16 years).
3. **Domain Slug Desynchronization**: A newly extracted fact or question using full PSI string names instead of machine slugs, breaking `gamb_exam.generator.generate_exam()`.
4. **Unrepresented Atomic Facts**: An atomic fact registered in `data/fact_inventory.json` with an empty `associated_question_ids` array, violating the 100% coverage guarantee.
5. **TSV / JSON Parity Drift**: A newly authored question added to `question_pool.json` without its corresponding entry appended to `anki/gamb_deck.tsv`, breaking line-to-ID alignment.

---

### Task 1: Re-Verify Primary Sources & Incorporate 1-Hop Satellite Criminal Statutes

**Files:**
- Create: `sources/ocga_satellites/16-6-3.md`
- Create: `sources/ocga_satellites/16-6-4.md`
- Create: `sources/ocga_satellites/16-6-5.md`
- Create: `sources/ocga_satellites/24-5-501.md`
- Modify: `sources/ocga_satellites/19-7-5.md`
- Modify: `MANIFEST.md`

**Interfaces:**
- Consumes: Official Georgia Code (LexisNexis GA Code portal / Justia GA Code 2024–2026 ed.)
- Produces: Complete, verified source markdown files for all syllabus statutes and 1-hop incorporated definitions.

- [ ] **Step 1: Fetch and document verified text for 1-hop incorporated statutes**

Fetch official Georgia code for:
- O.C.G.A. § 16-6-3 (Statutory rape: elements, age under 16, marriage exception, felony punishment for perpetrator 18+, misdemeanor Romeo & Juliet clause for perpetrator 16-18).
- O.C.G.A. § 16-6-4 (Child molestation: elements, child under 16, intent to arouse or satisfy sexual desires).
- O.C.G.A. § 16-6-5 (Enticing a child for indecent purposes: child under 16).
- O.C.G.A. § 24-5-501 (Privileged communications: attorney-client standard incorporated into § 24-9-21 for psychologist-patient).

Write these to `sources/ocga_satellites/16-6-3.md`, `sources/ocga_satellites/16-6-4.md`, `sources/ocga_satellites/16-6-5.md`, and `sources/ocga_satellites/24-5-501.md`.

- [ ] **Step 2: Cross-verify O.C.G.A. § 19-7-5, § 30-5-4, § 43-39, and Board Rules 510**

Inspect existing `sources/` against live references:
- Check `sources/ocga_satellites/19-7-5.md` to ensure subsection (b)(10) cross-references are explicit.
- Check `sources/ocga_43-39/` for complete text of 43-39-1 through 43-39-20.
- Check `sources/rules_510/department_510_full.txt` for Chapters 510-1 through 510-10.

- [ ] **Step 3: Update `MANIFEST.md`**

Update `MANIFEST.md` with the new satellite files, updated word counts, and verification dates.

- [ ] **Step 4: Commit primary source updates**

```bash
git add sources/ MANIFEST.md
git commit -m "feat(sources): add 1-hop incorporated criminal statutes and update source manifest"
```

---

### Task 2: Implement Fact Registry Schema & Automated Validation Suite

**Files:**
- Create: `gamb_exam/fact_registry.py`
- Create: `data/fact_inventory.json`
- Create: `tests/test_fact_inventory.py`

**Interfaces:**
- Consumes: `data/fact_inventory.json`, `gamb_exam/question_pool.json`, `anki/gamb_deck.tsv`
- Produces: `gamb_exam.fact_registry.load_facts()`, `validate_fact_inventory()`, `verify_fact_coverage()`

- [ ] **Step 1: Write failing tests for Fact Registry and Coverage Validation**

Write `tests/test_fact_inventory.py` asserting:
1. `test_fact_schema`: Every fact has non-empty `fact_id`, `source_type`, `citation`, valid `domain` slug, `subtopic`, `rule_summary`, `associated_question_ids`, `associated_anki_card_ids`.
2. `test_domain_slugs_valid`: Domains strictly match `{'licensure', 'privacy', 'prof-relationships', 'competence', 'assessment', 'recordkeeping'}`.
3. `test_100_percent_fact_coverage`: Asserts that `len(fact["associated_question_ids"]) >= 1` and `len(fact["associated_anki_card_ids"]) >= 1` for every fact.
4. `test_unique_fact_ids`: No duplicate `fact_id` strings.

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_fact_inventory.py -v`
Expected: FAIL (module or file not found).

- [ ] **Step 3: Implement `gamb_exam/fact_registry.py` and seed initial `data/fact_inventory.json`**

Implement helper functions:
- `load_facts(path: Path | None = None) -> list[dict]`
- `validate_fact_inventory(facts: list[dict], question_pool: list[dict], anki_lines: list[str]) -> list[str]` (returns list of error messages)
- Seed initial `data/fact_inventory.json` with a valid test fact so schema tests pass.

- [ ] **Step 4: Run test to verify it passes schema checks**

Run: `uv run pytest tests/test_fact_inventory.py -k "test_fact_schema or test_domain_slugs_valid or test_unique_fact_ids" -v`
Expected: PASS.

- [ ] **Step 5: Commit Fact Registry tooling**

```bash
git add gamb_exam/fact_registry.py data/fact_inventory.json tests/test_fact_inventory.py
git commit -m "feat(facts): add fact registry schema, loader, and validation suite"
```

---

### Task 3: Comprehensive Atomic Fact Extraction Across All Primary Sources

**Files:**
- Modify: `data/fact_inventory.json`

**Interfaces:**
- Consumes: All files in `sources/ocga_43-39/`, `sources/ocga_satellites/`, `sources/rules_510/`, and `sources/psi/`
- Produces: Complete inventory of 150+ discrete atomic testable facts with citations and parameters.

- [ ] **Step 1: Extract atomic facts from OCGA Title 43-39 (Psychologist Licensing Act)**
  - Board composition (6 members: 5 psychologists + 1 consumer), appointment by Governor, 5-year terms, removal.
  - License qualifications (doctoral degree, accredited program, 1500 predoc + 1500 postdoc hours).
  - Practice of psychology definition, psychological evaluation vs medical testing.
  - Title protection: use of "psychologist", "psychological", or "psychology".
  - Reciprocity and PSYPACT interjurisdictional practice (30-day temporary in-person rule, e-passport).
  - License renewal biennial cycle, expiration, reinstatement requirements.
  - Disciplinary sanctions, administrative hearings under APA, injunctions.

- [ ] **Step 2: Extract atomic facts from Department 510 Board Rules**
  - Chapter 510-1: Organization, Joint Secretary functions.
  - Chapter 510-2: Licensure requirements, examinations (EPPP + GAMB jurisprudence pass mark), internship/fellowship standards.
  - Chapter 510-3: Military spousal provisional licenses, temporary permits.
  - Chapter 510-4: Code of Conduct:
    - Competence, boundaries of competence, impairment recognition.
    - Multiple relationships, conflicts of interest, exploitation.
    - Sexual relationships: absolute ban with current clients; 2-year post-termination ban with onerous burden of proof under APA ethics.
    - Informed consent for therapy and assessment.
    - Test security, obsolete tests, scoring and release of test data.
    - Third-party requests, services to organizations, forensic role boundaries.
  - Chapter 510-5: Advertising, public statements, directory listings, prohibiting testimonials from current clients.
  - Chapter 510-6: Fees, financial arrangements, bartering restrictions, withholding records for non-payment prohibition in acute emergencies.
  - Chapter 510-7: Records retention (adults: 7 years from last contact; minors: 7 years past age of majority / age 25).
  - Chapter 510-8: Continuing education (40 hours per biennium; 6 hours in professional ethics; max 16 online/independent).
  - Chapter 510-9: Telepsychology guidelines, electronic practice security, emergency protocols across state lines.
  - Chapter 510-10: Joint Secretary fee schedule.

- [ ] **Step 3: Extract atomic facts from Satellite Codes & Mandatory Reporting**
  - O.C.G.A. § 19-7-5: Mandatory child abuse reporting within 24 hours, oral/written reporting to DFCS/law enforcement, immunity, misdemeanor failure to report penalty.
  - O.C.G.A. § 16-6-3: Statutory rape age thresholds (< 16 years old; perpetrator 18+ = felony; perpetrator 16–18 within 4 years = misdemeanor Romeo & Juliet).
  - O.C.G.A. § 16-6-4: Child molestation elements (< 16 years old).
  - O.C.G.A. § 16-6-5: Enticing child for indecent purposes (< 16 years old).
  - O.C.G.A. § 16-6-5.1: Sexual assault by therapist/supervisory authority on patient or supervisee (felony 1–25 years, lack of consent not required).
  - O.C.G.A. § 30-5-4: Mandatory reporting of abuse/neglect/exploitation of disabled adults and elder persons (65+), immediate reporting to DHS/Adult Protective Services.
  - O.C.G.A. § 37-3-41: Form 1013 involuntary psychiatric examination certificate (psychologist authority, 48-hour transport window, immunity for good faith).
  - O.C.G.A. § 24-9-21 & § 24-5-501: Psychologist-patient privilege placed on same basis as attorney-client privilege; exceptions (court-ordered exams, involuntary commitment, child abuse reporting, Tarasoff duty to warn under Georgia Bradley Center standard).
  - O.C.G.A. § 43-1-19 through § 43-1-27: General licensing board sanctions, subpoena powers, mandatory 10-day notice to Board upon felony conviction.
  - PSI Candidate Bulletin #1755: 60 questions total (50 scored + 10 unscored experimental), 60 minutes time limit, passing score 38 out of 50 (76%).

- [ ] **Step 4: Validate completeness of `data/fact_inventory.json`**

Run: `python -c "import json; facts = json.load(open('data/fact_inventory.json')); print(f'Total facts extracted: {len(facts)}')"`
Ensure facts span all 6 domains and all primary source statutes and rules.

- [ ] **Step 5: Commit Fact Inventory**

```bash
git add data/fact_inventory.json
git commit -m "feat(facts): populate comprehensive atomic fact inventory across all GAMB primary sources"
```

---

### Task 4: Audit & Renovate Existing Question Pool (Items 1–435) for Binary Balance & Fact Mapping

**Files:**
- Modify: `gamb_exam/question_pool.json`
- Modify: `tests/test_question_pool.py`

**Interfaces:**
- Consumes: `gamb_exam/question_pool.json`, `data/fact_inventory.json`
- Produces: Renovated `question_pool.json` with 2-Yes/2-No distractor balance, `fact_ids` mappings, and single definitive best answers.

- [ ] **Step 1: Write automated test to detect polar distractor imbalances**

Add to `tests/test_question_pool.py`:
- `test_no_polar_giveaways`: For any question whose options contain "Yes" and "No", verifies that the options have a balanced 2-Yes / 2-No split (or zero occurrences of Yes/No tokens). Flags any question with 3 Yes / 1 No or 3 No / 1 Yes.

- [ ] **Step 2: Run test to identify all defective questions**

Run: `uv run pytest tests/test_question_pool.py -k test_no_polar_giveaways -v`
Expected: List of questions failing the distractor balance rule.

- [ ] **Step 3: Renovate failing polar questions and map `fact_ids`**
  - For each flagged polar question:
    - Rewrite the distractors so there are exactly two plausible "Yes" options with distinct legal reasoning and two plausible "No" options with distinct statutory reasoning, OR
    - Reframe the question stem and options as direct legal declarations without "Yes/No" prefixes.
  - Assign corresponding `fact_ids` to existing questions (linking them to facts created in Task 3).
  - Update `data/fact_inventory.json` to record these linked `associated_question_ids`.

- [ ] **Step 4: Re-run tests to confirm all 435 questions pass distractor quality standards**

Run: `uv run pytest tests/test_question_pool.py -v`
Expected: 100% PASS.

- [ ] **Step 5: Commit question pool renovations**

```bash
git add gamb_exam/question_pool.json data/fact_inventory.json tests/test_question_pool.py
git commit -m "refactor(questions): renovate binary distractors and link existing question pool to fact inventory"
```

---

### Task 5: Question Pool Expansion & Anki Deck Synchronization

**Files:**
- Modify: `gamb_exam/question_pool.json`
- Modify: `anki/gamb_deck.tsv`
- Modify: `data/fact_inventory.json`
- Modify: `gamb_exam/seed.py`

**Interfaces:**
- Consumes: `data/fact_inventory.json`
- Produces: Expanded `question_pool.json` covering 100% of atomic facts; updated `anki/gamb_deck.tsv` maintaining 1:1 parity and fact tags.

- [ ] **Step 1: Identify uncovered atomic facts**

Run verification check to list all facts where `len(associated_question_ids) == 0`.

- [ ] **Step 2: Author new high-yield questions for all uncovered facts**
  - Author direct, rigorous questions for:
    - O.C.G.A. § 16-6-3: Statutory rape age brackets (< 16, perpetrator >= 18 felony vs 16-18 misdemeanor Romeo & Juliet defense).
    - O.C.G.A. § 16-6-4: Child molestation definition and age limit (< 16).
    - O.C.G.A. § 16-6-5: Enticing a child.
    - O.C.G.A. § 24-5-501 / § 24-9-21: Specific exceptions to psychologist privilege (Bradley Center duty to protect, court orders, Form 1013, child abuse).
    - Any newly uncovered Board Rules 510-1 through 510-10 provisions.
    - PSI Bulletin logistics (60 total questions, 10 experimental, 60 minutes, 38 passing score).
  - Assign sequential IDs ($436, 437, \dots, N$).
  - Ensure strict distractor congruity, tone, and single best answer.

- [ ] **Step 3: Generate synchronized Anki cards for new questions**
  - For each new question $M$, generate corresponding Anki card at line $M$ in `anki/gamb_deck.tsv`.
  - Columns: `Front \t Back \t Tags`.
  - Back includes direct answer, citation, and legal rationale.
  - Tags include domain, citation, and `fact:FACT-ID`.

- [ ] **Step 4: Update `associated_question_ids` and `associated_anki_card_ids` in `data/fact_inventory.json`**

Update the fact inventory so every single fact links to its corresponding question(s) and card(s).

- [ ] **Step 5: Run full coverage validation**

Run: `uv run pytest tests/test_fact_inventory.py -v`
Expected: PASS (100% fact coverage achieved).

- [ ] **Step 6: Commit pool expansion and Anki deck**

```bash
git add gamb_exam/question_pool.json anki/gamb_deck.tsv data/fact_inventory.json
git commit -m "feat(pool): expand question bank and Anki deck to achieve 100% fact inventory coverage"
```

---

### Task 6: Re-Seed Database, Rebuild Derived Assets & Full-Suite Verification

**Files:**
- Modify: `data/gamb_exam.db` (re-seeded)
- Modify: `docs/study_materials/` (compendium questions, keys, and cheat sheets)
- Run: `gamb_exam/seed.py`, `gamb_exam/build_assets.py`

**Interfaces:**
- Consumes: Expanded `gamb_exam/question_pool.json` and `anki/gamb_deck.tsv`
- Produces: Updated SQLite database and regenerated study compendiums.

- [ ] **Step 1: Re-seed SQLite database**

Run: `python -m gamb_exam.seed`
Expected: Confirms all $N$ questions loaded into SQLite `data/gamb_exam.db`.

- [ ] **Step 2: Rebuild study compendiums and markdown assets**

Run: `python -m gamb_exam.build_assets` (or asset compilation scripts) to update:
- `docs/study_materials/compendium_questions.md`
- `docs/study_materials/compendium_key.md`
- `docs/study_materials/practice_exam_form_a.md`, `form_b.md`, `form_c.md`
- `docs/study_materials/numbers_cheat_sheet.md`

- [ ] **Step 3: Run full automated test suite**

Run: `uv run pytest tests/ -v`
Expected: 100% of all unit, regression, generator, seed, pool, and fact inventory tests pass cleanly.

- [ ] **Step 4: Test interactive TUI / exam generator smoke test**

Run: `python -c "from gamb_exam.generator import generate_exam; exam = generate_exam(50); assert len(exam) == 50; print('Exam generation verified: 50 questions with valid domain quotas!')"`
Expected: Clean output confirming 50-question mock exam generation with valid domain distributions.

- [ ] **Step 5: Final commit**

```bash
git add data/ docs/study_materials/
git commit -m "chore(assets): re-seed database and regenerate compendium study assets"
```
