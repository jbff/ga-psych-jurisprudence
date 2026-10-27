# Georgia Psychology Jurisprudence Examination (GAMB) Cheat Sheets & Numerical Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the GAMB study aids by enriching the thematic Statutory Cheat Sheet and creating a standalone "All Numbers & Deadlines" cram sheet in Markdown and PDF, fully audited against O.C.G.A. statutes and Board Rules Chapter 510.

**Architecture:** Update `gamb_exam/build_assets.py` to add `generate_numbers_cheat_sheet` and expand `generate_cheat_sheet` with all audited statutory timeframes. Integrate both aids into `build_all_assets()`, update test suites in `tests/test_build_assets.py` and `tests/test_cli.py`, and run the build pipeline to generate the artifacts into `docs/study_materials/` and `pdfs/`.

**Tech Stack:** Python 3.14, WeasyPrint (HTML-to-PDF compiler), Pytest, Click CLI, Markdown.

---

### Task 1: Write Unit Tests for Enhanced `generate_cheat_sheet` and New `generate_numbers_cheat_sheet`

**Files:**
- Modify: `tests/test_build_assets.py:17-53`
- Modify: `tests/test_build_assets.py:403-421`

- [ ] **Step 1: Update `tests/test_build_assets.py` with tests for both cheat sheets**

Add imports and new test function `test_generate_numbers_cheat_sheet`, and update assertions in `test_generate_cheat_sheet` and `test_build_all_assets`:

```python
from gamb_exam.build_assets import (
    build_all_assets,
    compile_html_to_pdf,
    generate_cheat_sheet,
    generate_numbers_cheat_sheet,
    generate_compendium,
    generate_practice_forms,
    generate_web_quizzer,
)


def test_generate_cheat_sheet(tmp_path: Path):
    md_path = tmp_path / "cheat_sheet.md"
    html_path = tmp_path / "cheat_sheet.html"
    pdf_path = tmp_path / "cheat_sheet.pdf"

    generate_cheat_sheet(md_path=md_path, html_path=html_path)

    assert md_path.exists()
    assert html_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "Georgia Psychology Jurisprudence Examination" in content
    assert "Statutory Quick-Reference Cheat Sheet" in content
    assert "O.C.G.A. § 19-7-5" in content
    assert "O.C.G.A. § 43-39-16" in content
    assert "40 hours" in content
    assert "48 hours" in content
    assert "7 days" in content
    assert "72 hours" in content
    assert "10 days" in content
    assert "5 days" in content
    assert "30 days" in content
    assert "540 hours" in content

    html_content = html_path.read_text(encoding="utf-8")
    assert "Georgia Psychology Jurisprudence Examination" in html_content
    assert "48 hours" in html_content
    assert "7 days" in html_content

    compile_html_to_pdf(html_path, pdf_path)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 5000


def test_generate_numbers_cheat_sheet(tmp_path: Path):
    md_path = tmp_path / "numbers_cheat_sheet.md"
    html_path = tmp_path / "numbers_cheat_sheet.html"
    pdf_path = tmp_path / "numbers_cheat_sheet.pdf"

    generate_numbers_cheat_sheet(md_path=md_path, html_path=html_path)

    assert md_path.exists()
    assert html_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "Numbers, Deadlines & Supervision Ratios" in content
    assert "24 Hours" in content
    assert "48 Hours" in content
    assert "72 Hours" in content
    assert "5 Days" in content
    assert "7 Days" in content
    assert "10 Days" in content
    assert "30 Days" in content
    assert "31 Days" in content
    assert "60 Days" in content
    assert "120 Days" in content
    assert "11 to 24 Months" in content
    assert "540 hours" in content
    assert "1,500 hours" in content
    assert "1:30" in content
    assert "1:20" in content

    html_content = html_path.read_text(encoding="utf-8")
    assert "Numbers, Deadlines & Supervision Ratios" in html_content
    assert "48 Hours" in html_content
    assert "72 Hours" in html_content

    compile_html_to_pdf(html_path, pdf_path)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 5000
```

And in `test_build_all_assets`:
```python
    assert len(artifacts["pdfs"]) == 6
    assert len(artifacts["docs"]) == 7
    assert len(artifacts["web"]) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_build_assets.py::test_generate_numbers_cheat_sheet -v`
Expected: FAIL with `ImportError: cannot import name 'generate_numbers_cheat_sheet'`

---

### Task 2: Implement Enhanced `generate_cheat_sheet` and `generate_numbers_cheat_sheet` in `gamb_exam/build_assets.py`

**Files:**
- Modify: `gamb_exam/build_assets.py:230-345` (and around `build_all_assets`)

- [ ] **Step 1: Enhance `generate_cheat_sheet` in `gamb_exam/build_assets.py`**

Update `generate_cheat_sheet` to include all audited parameters across the 4 thematic sections:
1. Section 1: Pre-doc internship (1,500 hrs / 500 direct client contact); Doctoral residency (540 in-person hrs / 1 yr); SWE (1,500 hrs, 11-24 mo, 500 direct client contact); Supervision ratios (1:30 SWE, 1:20 clinical, max 3 supervisees); Senior Psychologist (10 yrs licensure); Endorsement practice equivalent (3 yrs full-time, 30 hrs/wk, 50 wks/yr); Failed GAMB retake (30 days); EPPP failure remediation (3 fails -> 3 sem hrs / 15 CE; 6 fails -> 9 sem hrs / 45 CE); Biennial CE (40 hrs total, 6 ethics Area I live, min 20 Area I, max 16 Area II); Late renewal penalty period (31 days, Jan 1-31); CE audit cure period (31 days).
2. Section 2: Form 1013 involuntary exam personal examination window (within preceding 48 hours); Form 1013 certificate validity (7 days); Peace officer custody execution window (within 72 hours of receiving certificate); Court apprehension order affiant observation window (within preceding 48 hours); Court order validity (7 days); Child abuse mandatory reporting (immediately, no later than 24 hours); Elder / disabled adult abuse mandatory reporting (APS/police) and police forwarding window (24 hours).
3. Section 3: Psychologist-client privilege (identical to attorney-client privilege O.C.G.A. § 43-39-16 / § 24-5-501); Sexual misconduct 1st degree (felony, 1-25 yrs, $100k fine); Sexual misconduct 2nd degree (high & aggravated misdemeanor); Defense of consent prohibited; Former client sexual contact moratorium (2 years post-termination).
4. Section 4: Clinical records retention (adult: min 7 yrs; minor: min 7 yrs past age of majority = age 25); Out-of-state practice (max 30 days/calendar year, requires ≥5 days advance written notice to Board); PSYPACT IPC practice (max 30 days/calendar year); Mandatory conviction reporting (within 10 days for felonies and drug convictions); Board civil fines (max $500/violation); Unlicensed practice criminal penalty ($100-$1,000 fine and/or up to 12 months jail); Appeals to Superior Court of Fulton County ("any evidence" standard).

Generate corresponding HTML table layout matching Markdown.

- [ ] **Step 2: Implement `generate_numbers_cheat_sheet` in `gamb_exam/build_assets.py`**

Create `generate_numbers_cheat_sheet(md_path: Path, html_path: Path) -> None` with the dedicated chronological tables:
1. Table 1: The Clock — Hours (24 hrs, 48 hrs, 72 hrs).
2. Table 2: The Calendar — Days (5 days, 7 days, 10 days, 30 days, 31 days, 60 days, 120 days).
3. Table 3: Months & Years (6 months, 11 to 24 months, 12 months / 1 year, 24 months / 2 years, 3 years, 5 years, 7 years / Age 25, 10 years).
4. Table 4: Training Hours, Supervision Ratios & Board Standards (1:30 SWE, 1:20 Clinical, Max 3 Supervisees; 40 CE, 6 Ethics, 20 Area I, 16 Area II; 1,500 Internship, 1,500 SWE, 500 Direct Client, 540 Residency; 3 & 6 EPPP Retake Remediation; 6 Board Members, 5-yr term, Quorum 4; 75% Passing Scores; $500 Max Civil Fine).

Generate both Markdown and HTML representations with matching print styling.

- [ ] **Step 3: Update `build_all_assets()` in `gamb_exam/build_assets.py`**

In `build_all_assets()`:
- Add generation of `numbers_cheat_sheet_md = docs_dir / "numbers_cheat_sheet.md"`, `numbers_cheat_sheet_html = docs_dir / "numbers_cheat_sheet.html"`, `numbers_cheat_sheet_pdf = pdfs_dir / "GAMB_Numbers_And_Deadlines_Cheat_Sheet.pdf"`.
- Invoke `generate_numbers_cheat_sheet(numbers_cheat_sheet_md, numbers_cheat_sheet_html)`.
- Invoke `compile_html_to_pdf(numbers_cheat_sheet_html, numbers_cheat_sheet_pdf)`.
- Unlink temporary HTML.
- Append new PDF to `artifacts["pdfs"]` and new MD to `artifacts["docs"]`.

- [ ] **Step 4: Run unit tests to verify they pass**

Run: `uv run pytest tests/test_build_assets.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add gamb_exam/build_assets.py tests/test_build_assets.py
git commit -m "feat(assets): enrich statutory cheat sheet and add numbers & deadlines cram sheet"
```

---

### Task 3: Update CLI Tests and Regenerate All Asset Files

**Files:**
- Modify: `tests/test_cli.py:382-392`
- Generate: `docs/study_materials/cheat_sheet.md`
- Generate: `docs/study_materials/numbers_cheat_sheet.md`
- Generate: `pdfs/GAMB_Statutory_Cheat_Sheet.pdf`
- Generate: `pdfs/GAMB_Numbers_And_Deadlines_Cheat_Sheet.pdf`

- [ ] **Step 1: Update assertions in `tests/test_cli.py`**

In `test_build_assets_cli_success`:
Add:
```python
    assert (tmp_path / "pdfs" / "GAMB_Numbers_And_Deadlines_Cheat_Sheet.pdf").exists()
    assert (tmp_path / "docs" / "study_materials" / "numbers_cheat_sheet.md").exists()
```

- [ ] **Step 2: Run CLI test to verify it passes**

Run: `uv run pytest tests/test_cli.py -k test_build_assets -v`
Expected: PASS

- [ ] **Step 3: Run full asset generation CLI**

Run: `uv run gamb-exam build-assets`
Expected: Successfully generates all 6 PDFs, 7 Markdown docs, and 1 Web application.

- [ ] **Step 4: Verify generated files and content**

Run: `ls -lh pdfs/ docs/study_materials/`
Verify `pdfs/GAMB_Numbers_And_Deadlines_Cheat_Sheet.pdf` and `docs/study_materials/numbers_cheat_sheet.md` exist and are populated.

- [ ] **Step 5: Run full test suite**

Run: `uv run pytest`
Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add tests/test_cli.py docs/study_materials/ pdfs/
git commit -m "feat(build): generate updated statutory cheat sheet and numbers cram sheet assets"
```
