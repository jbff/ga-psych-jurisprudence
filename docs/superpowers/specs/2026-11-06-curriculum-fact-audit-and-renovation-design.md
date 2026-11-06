# Design Specification: Curriculum Fact Audit, Source Re-Verification & Question Bank Renovation

**Date**: 2026-11-06  
**Status**: Pending Review  
**Topic**: Comprehensive Georgia Psychology Jurisprudence (GAMB) Primary Source Audit, Atomic Fact Extraction, Distractor Balancing, and Question/Anki Pool Renovation

---

## 1. Intent & The Why

A candidate taking the official Georgia Psychology Jurisprudence Examination administered by PSI encounters 60 questions (50 scored items across 6 core domains + 10 unscored experimental pretest items) in 60 minutes. While our existing study toolkit (435 curated questions and matching Anki cards) proved effective for passing the examination, actual test items frequently assess fine-grained statutory nuances, age brackets, and cross-referenced definitions (e.g., statutory sexual abuse age pairings from the criminal code embedded into child abuse reporting statutes).

To ensure that any future candidate who masters this toolkit has every legal and regulatory fact needed to reason through any test scenario, we are performing an independent, end-to-end curriculum audit. We will re-verify all official primary sources, extract an atomic inventory of every testable fact, repair all unbalanced binary distractors, and expand both the question pool and Anki deck until 100% of testable facts are accounted for.

---

## 2. Goals, Non-Goals & Anti-Goals

### Goals
1. **Independent Primary Source Verification**: Re-verify and re-acquire authentic, current statutory text and administrative rules from official state portals:
   - LexisNexis Georgia Code (Official Code of Georgia Annotated)
   - Georgia Secretary of State / Rules and Regulations of the State of Georgia (Department 510)
   - PSI Candidate Information Bulletin #1755
2. **Explicit Resolution of Cited Sub-Statutes (1-Hop Substantive Boundary Filter)**:
   - When a primary statute or rule in the PSI syllabus establishes a duty, standard, or definition by incorporating another Georgia code section (e.g., O.C.G.A. § 19-7-5 defining reportable sexual abuse via criminal code sections like § 16-6-3, § 16-6-4, § 16-6-5; O.C.G.A. § 24-9-21 adopting the § 24-5-501 attorney-client standard; O.C.G.A. § 37-3-41 adopting mental illness inpatient standards), we import the **specific definitions, threshold elements (e.g., age brackets, relationships, and criteria)** required to evaluate that duty.
   - **Boundary Filter (Preventing Scope Creep)**: We evaluate cross-references using a strict 1-hop filter: only substantive definitions and elements directly necessary to apply the primary duty are imported as testable facts. We do not follow secondary/multi-hop references or import ancillary criminal procedures, general sentencing tables, or unrelated penal provisions.
3. **Atomic Fact Inventory (`data/fact_inventory.json`)**: Establish a permanent, structured registry of discrete, testable legal/regulatory facts (statutory numbers, timeframes, reporting duties, authorized agencies, exceptions, definitions, and prohibited conduct).
4. **Distractor Quality & Balance Overhaul**:
   - For all polar/binary questions, ensure balanced distractor rationale splits (e.g., exactly two "Yes, because..." and two "No, because..." options) or rephrase the choices as direct premise-based assertions without "Yes/No" giveaway cues.
   - Strictly guarantee that every question has one, and only one, best legal answer under Georgia law.
   - Use negative-stem phrasing ("Which of the following is NOT...", "All of the following EXCEPT...") only where naturally suited to the statutory provision (no arbitrary percentage quota).
5. **Full Curriculum Coverage & Synchronization**:
   - Expand `gamb_exam/question_pool.json` to cover 100% of atomic facts.
   - Synchronize all corresponding items into the Anki deck (`anki/gamb_deck.tsv`).
   - Rebuild derived study assets (SQLite DB via `gamb_exam/seed.py`, compendium documents, and test forms).

### Non-Goals
- **Synthetic Clinical Scenario Generation**: We will *not* invent fictional narrative clinical vignettes or simulated case stories. The focus is strictly on comprehensive mastery of the underlying statutory facts, definitions, and rules so the student can independently deduce the answer to any vignette.
- **Arbitrary Negative-Stem Quotas**: No mandatory percentage of "NOT/EXCEPT" stems. They will be used judiciously when the statute itself is structured as a list of exceptions or exclusions.
- **Rewriting Doverspike Commentary**: Dr. Doverspike's study guide will remain a secondary crosswalk reference, not a replacement for statutory and rule text.

### Anti-Goals
- **Distractor Giveaways**: Eliminating "3 Yes / 1 No" or "3 No / 1 Yes" answer sets where the isolated polarity gives away the correct answer without reading the legal explanation.
- **Unverified Third-Party Claims**: No facts will be added based on third-party memory or unverified summaries without direct citation to the official O.C.G.A. statute or Board Rule 510.

---

## 3. Approaches Considered & Trade-Offs

### Approach 1: Fact-Inventory Matrix First, Then Cross-Audit & Expansion (Selected)
- **Workflow**:
  1. Independently re-verify primary sources against official Georgia portals, adding cited satellite definitions.
  2. Extract an exhaustive atomic fact inventory (`data/fact_inventory.json`).
  3. Audit existing 435 questions against the fact inventory, fixing binary distractors and citations.
  4. Generate new direct questions and Anki flashcards for all unmapped facts until coverage hits 100%.
- **Trade-offs**: Requires disciplined upfront fact extraction, but provides an auditable, verifiable coverage matrix that mathematically proves completeness.

### Approach 2: Section-by-Section In-Place Expansion
- **Workflow**: Walk through existing markdown source files in order, checking online text, updating questions on the fly, and adding missing items file by file.
- **Trade-offs**: Faster initial edits to the question pool, but lacks a centralized fact matrix, making it prone to missing cross-statutory overlaps and leaving overall coverage uncertain.

### Approach 3: Clean-Slate Rebuild
- **Workflow**: Archive all 435 questions and build a brand-new pool and Anki deck from scratch from new fact extractions.
- **Trade-offs**: Avoids modifying legacy items, but discards hundreds of verified, high-yield questions and explanations that directly contributed to exam success.

*Selected*: **Approach 1**, as chosen by the user, for maximum rigor, auditable completeness, and preservation of proven study items.

---

## 4. Architectural & Implementation Specifications

### A. Primary Source Corpus Verification & Expansion
The following official syllabus must be verified against live state sources and updated on disk in `sources/`:

1. **Core Psychology Licensing Act**:
   - `OCGA 43-39-1` through `OCGA 43-39-20` (Georgia Board of Examiners of Psychologists).
2. **Board Rules & Regulations**:
   - Department 510 Rules: Chapters 510-1 through 510-10 (General Provisions, Licensure, Code of Conduct, Continuing Education, Fees, etc.).
3. **General Licensing Provisions**:
   - `OCGA 43-1-19` through `OCGA 43-1-27` (Joint Secretary / Professional Licensing Boards general authority, disciplinary actions, felony convictions).
4. **Mandatory Reporting & Satellite Statutes**:
   - `OCGA 19-7-5`: Reporting of child abuse (must be updated/verified with full statutory definitions).
   - `OCGA 30-5-4`: Protection of disabled adults and elder persons reporting.
   - `OCGA 37-3-41`: Emergency admission / involuntary commitment (Form 1013 authority and immunity).
   - `OCGA 24-9-21` & `OCGA 24-5-501`: Psychologist-patient privileged communications (attorney-client standard and statutory exceptions).
   - `OCGA 31-7-160` through `31-7-165`: Peer review and health care facility reporting.
   - `OCGA 16-13-110` through `16-13-114`: Controlled substances reporting and patient record security.
   - `OCGA 16-6-5.1`: Sexual assault by person with supervisory/disciplinary authority (psychotherapist-patient).
5. **Incorporated Cross-References (New Satellites to Add)**:
   - `OCGA 16-6-3`: Statutory rape elements, age of victim (< 16), age of perpetrator (>= 18 for felony, 16–18 misdemeanor/Romeo & Juliet provisions).
   - `OCGA 16-6-4`: Child molestation elements and definitions.
   - `OCGA 16-6-5`: Enticing a child for indecent purposes.

### B. Atomic Fact Inventory Schema (`data/fact_inventory.json`)
Every distinct, legally testable rule or requirement is assigned an atomic fact record:

```json
[
  {
    "fact_id": "FACT-19-7-5-014",
    "source_type": "OCGA",
    "citation": "O.C.G.A. § 19-7-5(b)(10)(C) & § 16-6-3",
    "domain": "licensure",
    "domain_display": "Licensure and Regulations",
    "subtopic": "Reporting Child Abuse",
    "rule_summary": "Under Georgia law, statutory rape proscribed under OCGA 16-6-3 constitutes sexual abuse for mandatory child abuse reporting: it occurs when a person engages in sexual intercourse with a person under 16 years of age who is not their spouse.",
    "key_parameters": {
      "age_threshold": 16,
      "statutory_reference": "OCGA 16-6-3"
    },
    "associated_question_ids": [436],
    "associated_anki_card_ids": [436],
    "audit_status": "verified"
  }
]
```

*Design Decisions Settled*:
1. **Domain Taxonomy**: Uses existing codebase machine slugs (`licensure`, `privacy`, `prof-relationships`, `competence`, `assessment`, `recordkeeping`) for programmatic compatibility with `generator.py`, `db.py`, and test suites, while retaining `domain_display` for human/PSI reporting.
2. **Cardinality & Sync Parity**:
   - `associated_question_ids` and `associated_anki_card_ids` are arrays (`list[int]`).
   - `question_pool.json` maintains strict 1:1 numerical index parity with `anki/gamb_deck.tsv` (question ID $N$ maps directly to line $N$ in the deck).
   - `anki/gamb_deck.tsv` retains its strict 3-column structure (`Front \t Back \t Tags`), appending the fact ID tag (e.g. `fact:FACT-19-7-5-014`) into the space-delimited `Tags` column to avoid breaking existing TSV parsers and Anki import workflows.
   - `question_pool.json` receives an optional `fact_ids: list[str]` field on each item.
3. **Coverage Directionality**:
   - **Primary Mandate (100% Fact Coverage)**: Every atomic fact in `fact_inventory.json` must link to at least one question and Anki card.
   - **Legacy Mapping**: All statutory, regulatory, and PSI bulletin test questions in the existing 435-item pool map directly to their corresponding atomic fact in `fact_inventory.json`. Any legacy items testing general ethics or test logistics are assigned corresponding primary source fact records (e.g. from the PSI Candidate Bulletin or Board Rule 510-4).

### C. Question Pool Standards (`gamb_exam/question_pool.json`)
1. **Distractor Congruity**:
   - All 4 options must be grammatical and substantive answers to the question stem.
   - No obvious length or syntactical outliers.
2. **Polar / Binary Balance**:
   - For any question testing whether an action is permitted, prohibited, required, or privileged:
     - Either use **2 Yes / 2 No** options with distinct, legally plausible rationales:
       - `A`: Yes, because [Valid reason or Common misconception 1]
       - `B`: Yes, because [Alternative misconception 2]
       - `C`: No, because [Valid statutory reason] (CORRECT)
       - `D`: No, because [Alternative statutory misconception 3]
     - Or formulate the question and options as direct legal declarations without "Yes/No" tokens.
3. **Single Definitive Answer**: Exactly one option is legally correct under Georgia law.
4. **Authoritative Explanations**: Every question's explanation must cite the specific statute or rule section and explain why the correct answer is mandated and why each distractor is legally invalid.

### D. Anki Deck Standards (`anki/gamb_deck.tsv`)
- TSV format compatible with Anki import (`Front <tab> Back <tab> Tags`).
- Front contains clear, unambiguous factual or legal question prompt.
- Back contains concise direct answer, statutory citation, and key legal rationale.
- Tagged by domain, citation, and fact ID.

---

## 5. Verification & Test Strategy

1. **Schema & Integrity Validation**:
   - Automated pytest suite verifying `gamb_exam/question_pool.json`:
     - IDs are unique and sequential.
     - Exactly 4 options (`A`, `B`, `C`, `D`).
     - `correct_option` is valid.
     - No blank fields or orphaned questions.
     - No binary distractor imbalances (flagging any question with 3 Yes / 1 No or 3 No / 1 Yes).
2. **Coverage Verification**:
   - Automated check confirming every entry in `data/fact_inventory.json` is linked to at least one question in `gamb_exam/question_pool.json` and one card in `anki/gamb_deck.tsv`.
3. **Seed & TUI Verification**:
   - Running `python -m gamb_exam.seed` and running exam generator smoke tests to verify clean database insertion and exam generation without errors.
4. **Anki Deck Parity**:
   - Script verifying 1:1 count and content parity between `question_pool.json` and `anki/gamb_deck.tsv`.

---

## 6. What Is Left to the Builder

- Exact division of batch sizes when reviewing the fact inventory and questions.
- Specific phrasing of newly authored question stems and distractors, provided they strictly comply with Section 4.
- Exact styling of the fact inventory JSON/Markdown tooling and scripts.
