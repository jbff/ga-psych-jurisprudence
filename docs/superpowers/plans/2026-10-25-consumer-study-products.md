# Consumer-Friendly Study Products & Web Quizzer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, test, and package zero-install consumer-ready study products (PDF cheat sheet, 435-question domain compendium, 3 practice exam booklets with separate keys, and a standalone single-file offline Web Quizzer) and prominently feature them in `README.md`.

**Architecture:** A deterministic build engine in `gamb_exam/build_assets.py` compiles `gamb_exam/question_pool.json` into semantic HTML/CSS print stylesheets, rendered into vector PDFs via WeasyPrint, and bundles a self-contained responsive offline web application in `web/index.html`. Sourced via a new `gamb-exam build-assets` CLI subcommand.

**Tech Stack:** Python 3.10+, WeasyPrint, HTML5, CSS Paged Media (`@page`), Vanilla JavaScript (ES6+), SQLite, Pytest.

---

### Task 1: Build Pipeline Infrastructure & Statutory Cheat Sheet Generation

**Files:**
- Create: `gamb_exam/build_assets.py`
- Create: `tests/test_build_assets.py`
- Output: `pdfs/GAMB_Statutory_Cheat_Sheet.pdf`
- Output: `docs/study_materials/cheat_sheet.md`

- [ ] **Step 1: Write failing test for cheat sheet generation**

Create `tests/test_build_assets.py`:
```python
from pathlib import Path
import pytest
from gamb_exam.build_assets import generate_cheat_sheet, compile_html_to_pdf

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

    # Test PDF compilation
    compile_html_to_pdf(html_path, pdf_path)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 5000  # Non-trivial PDF size
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_build_assets.py::test_generate_cheat_sheet -v`  
Expected: FAIL (`ModuleNotFoundError: No module named 'gamb_exam.build_assets'`).

- [ ] **Step 3: Implement `compile_html_to_pdf` and `generate_cheat_sheet` in `gamb_exam/build_assets.py`**

Create `gamb_exam/build_assets.py`:
```python
"""Asset generation pipeline for Georgia Psychology Jurisprudence Examination study products."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from gamb_exam.generator import LEGAL_DISCLAIMER

PRINT_CSS = """
@page {
    size: letter;
    margin: 0.75in 0.75in 0.85in 0.75in;
    @top-right {
        content: "GAMB Study Guide";
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 8pt;
        color: #718096;
    }
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 8pt;
        color: #718096;
    }
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.45;
    color: #1a202c;
    font-size: 10pt;
    margin: 0;
    padding: 0;
}

h1 {
    font-size: 18pt;
    color: #1a365d;
    border-bottom: 2pt solid #2b6cb0;
    padding-bottom: 4pt;
    margin-top: 0;
    margin-bottom: 8pt;
}

h2 {
    font-size: 13pt;
    color: #2c5282;
    margin-top: 14pt;
    margin-bottom: 6pt;
    border-bottom: 1pt solid #e2e8f0;
    padding-bottom: 2pt;
    page-break-after: avoid;
}

h3 {
    font-size: 11pt;
    color: #2b6cb0;
    margin-top: 10pt;
    margin-bottom: 4pt;
    page-break-after: avoid;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 6pt;
    margin-bottom: 10pt;
    page-break-inside: avoid;
    font-size: 9pt;
}

th, td {
    border: 1pt solid #cbd5e0;
    padding: 4pt 6pt;
    text-align: left;
    vertical-align: top;
}

th {
    background-color: #ebf8ff;
    color: #2c5282;
    font-weight: bold;
}

tr:nth-child(even) td {
    background-color: #f7fafc;
}

.disclaimer {
    background-color: #fffaf0;
    border-left: 3pt solid #dd6b20;
    padding: 6pt 8pt;
    margin-bottom: 12pt;
    font-size: 8pt;
    color: #7b341e;
    page-break-inside: avoid;
}

.question-block {
    margin-bottom: 10pt;
    page-break-inside: avoid;
    border-bottom: 0.5pt solid #edf2f7;
    padding-bottom: 6pt;
}

.question-text {
    font-weight: 600;
    margin-bottom: 4pt;
    color: #2d3748;
}

.option {
    margin-left: 12pt;
    margin-bottom: 2pt;
    font-size: 9.5pt;
}

.key-block {
    margin-bottom: 8pt;
    page-break-inside: avoid;
    border-left: 2pt solid #3182ce;
    padding-left: 6pt;
}

.badge {
    display: inline-block;
    padding: 1pt 4pt;
    font-size: 8pt;
    font-weight: bold;
    border-radius: 3pt;
    background-color: #e2e8f0;
    color: #4a5568;
}

.page-break {
    page-break-before: always;
}
"""


def compile_html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    """Compile an HTML file to PDF using WeasyPrint with graceful error handling."""
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    weasyprint_bin = shutil.which("weasyprint")
    if weasyprint_bin:
        cmd = [weasyprint_bin, str(html_path), str(pdf_path)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"WeasyPrint failed ({res.returncode}): {res.stderr}")
    else:
        try:
            import weasyprint
            weasyprint.HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        except ImportError as err:
            raise RuntimeError("Neither weasyprint CLI binary nor weasyprint Python package is available") from err


def generate_cheat_sheet(md_path: Path, html_path: Path) -> None:
    """Generate the high-yield Statutory Quick-Reference Cheat Sheet in Markdown and HTML."""
    md_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)

    md_content = f"""# Georgia Psychology Jurisprudence Examination (GAMB)
## High-Yield Statutory Quick-Reference Cheat Sheet

{LEGAL_DISCLAIMER}

---

### 1. Licensure, Supervision & Continuing Education (Rule 510-8 & 510-2)

| Parameter | Statutory / Rule Requirement | Legal Authority |
| :--- | :--- | :--- |
| **Total Biennial CE** | **40 hours** every 2 years (ending Dec 31 of even years) | Rule 510-8-.01 |
| **Ethics CE Requirement** | **6 hours** in professional ethics (Area I, live/synchronous) | Rule 510-8-.01 |
| **Area I CE (Live/Interactive)** | **Minimum 20 hours** required (no maximum; all 40 may be Area I) | Rule 510-8-.02 |
| **Area II CE (Self-Study/Courses)** | **Maximum 16 hours** permitted per biennium | Rule 510-8-.02 |
| **Academic Coursework CE** | 10 hrs per semester course (max 20 hrs per biennium) | Rule 510-8-.02 |
| **Peer-Reviewed Authorship CE** | 10 hrs for 1st or 2nd author of peer-reviewed article | Rule 510-8-.02 |
| **First-Time Workshop Presentation** | 1 hr CE per hour taught (max 6 hrs per presentation) | Rule 510-8-.02 |
| **Pre-Doctoral Internship** | Minimum **1,500 hours** in an organized training program | Rule 510-2-.04 |
| **Post-Doctoral SWE** | Minimum **1,500 hours** (or 2,000 hrs if prior to deg conferral) | Rule 510-2-.05 |
| **Max Supervisees** | Maximum **3 supervisees** concurrently without prior Board approval | Rule 510-5-.06 |
| **License Expiration & Late Period** | Dec 31 of even years; 31-day late penalty period (Jan 1–31) | Rule 510-7-.01 |
| **Reinstatement After Lapse** | Formal application, fees, and 40 CE hours within past 2 years | Rule 510-7-.03 |

---

### 2. Mandatory Reporting Overrides & Emergency Commitment

| Category | Legal Rule & Action Required | Statute |
| :--- | :--- | :--- |
| **Child Abuse Reporting** | Mandatory reporting **immediately**, and in no case later than **24 hours** after forming suspicion. Report to DFCS or local law enforcement/prosecutor. | **O.C.G.A. § 19-7-5** |
| **Child Abuse Privilege** | Psychologist-client privilege is **abrogated**; cannot shield child abuse. | O.C.G.A. § 19-7-5(f) |
| **Child Abuse Penalty** | Knowing and willful failure to report is a **misdemeanor**. | O.C.G.A. § 19-7-5(h) |
| **Child Abuse Immunity** | Broad **good-faith immunity** from civil and criminal liability. | O.C.G.A. § 19-7-5(f) |
| **Elder / Disabled Abuse** | Mandatory reporting of abuse, neglect, or exploitation to Adult Protective Services (DHS) or police. Law enforcement must forward report within 24 hrs. Privilege abrogated. | **O.C.G.A. § 30-5-4** |
| **Involuntary Exam (Form 1013)** | Licensed psychologists have statutory authority to execute Form 1013 certificate upon determining imminent danger or grave disability. | **O.C.G.A. § 37-3-41** |
| **Peace Officer 1013 Execution** | Peace officers must take individual into custody within **72 hours** of certificate execution and deliver to emergency receiving facility. | O.C.G.A. § 37-3-41(a) |

---

### 3. Confidentiality, Privilege & Prohibited Relationships

| Subject | Statutory Standard | Authority |
| :--- | :--- | :--- |
| **Confidential Communications** | Communications between licensed psychologist and client are placed on the **identical legal basis as attorney-client privilege**. | **O.C.G.A. § 43-39-16**; § 24-5-501 |
| **Sexual Misconduct (1st Degree)** | Sexual intercourse, cunnilingus, fellatio, or anilingus with a client/patient: **Felony (1 to 25 years imprisonment, up to $100,000 fine)**. | **O.C.G.A. § 16-6-5.1** |
| **Sexual Misconduct (2nd Degree)** | Any other sexual contact with a client/patient: **Misdemeanor of a high and aggravated nature**. | O.C.G.A. § 16-6-5.1 |
| **Defense of Consent** | **Consent of the victim is NOT a defense** to prosecution for psychotherapist sexual misconduct under Georgia law. | O.C.G.A. § 16-6-5.1(b) |
| **Former Client Sexual Contact** | Prohibited for at least **2 years** following cessation of professional services under APA Ethics Code (Standard 10.08). | Rule 510-4-.02 |

---

### 4. Recordkeeping, Practice Limits & Penalties

| Topic | Legal Rule | Authority |
| :--- | :--- | :--- |
| **Adult Record Retention** | Minimum **7 years** following date of last clinical service. | APA 6.01; Rule 510-4 |
| **Minor Record Retention** | Minimum **7 years past the age of majority** (age 25 total). | APA 6.01; Rule 510-4 |
| **Withholding Emergency Records** | **Prohibited**: Records needed for emergency treatment cannot be withheld solely for nonpayment of fees. | APA Standard 6.03 |
| **Bartering** | Permissible **only if not clinically contraindicated** and not exploitative. | APA Standard 6.05 |
| **Test Data vs. Test Materials** | Test data (raw scores, answers) releasable with client consent; Test materials (manuals, test booklets) protected to preserve test security. | APA Standards 9.04, 9.11 |
| **Out-of-State Practice** | Non-resident licensed psychologists may practice in Georgia up to **30 days per calendar year** with Board notification/approval. | O.C.G.A. § 43-39-7(8) |
| **PSYPACT Practice** | Unlimited telepsychology under E.Passport; up to 30 days temporary in-person practice under Interjurisdictional Practice Certificate (IPC). | O.C.G.A. § 43-39-20 |
| **Board Civil Fines** | Maximum civil fine not to exceed **$500.00 per violation**. | O.C.G.A. § 43-1-19(d)(7) |
| **Unlicensed Practice Penalty** | Criminal misdemeanor: **$100 to $1,000 fine and/or up to 12 months jail**. | O.C.G.A. § 43-39-17 |
| **Appeal of Board Decision** | Appeal must be filed in **Superior Court of Fulton County** under the Georgia Administrative Procedure Act ("any evidence" standard). | O.C.G.A. § 43-39-13; § 50-13-19 |
"""
    md_path.write_text(md_content, encoding="utf-8")

    # Render HTML with print CSS
    import markdown
    html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>GAMB Statutory Quick-Reference Cheat Sheet</title>
<style>
{PRINT_CSS}
</style>
</head>
<body>
<h1>Georgia Psychology Jurisprudence Examination (GAMB)</h1>
<div class="badge">STATUTORY QUICK-REFERENCE CRAM SHEET</div>
<div class="disclaimer">
<strong>LEGAL & REGULATORY DISCLAIMER:</strong> This reference sheet is an independently authored study aid and is NOT official examination material from the Georgia Board or PSI Services. Verified against O.C.G.A. and Board Rules Chapter 510.
</div>

<h2>1. Licensure, Supervision & Continuing Education (Rule 510-8 & 510-2)</h2>
<table>
<thead><tr><th>Parameter</th><th>Statutory / Rule Requirement</th><th>Legal Authority</th></tr></thead>
<tbody>
<tr><td><strong>Total Biennial CE</strong></td><td><strong>40 hours</strong> every 2 years (ending Dec 31 of even years)</td><td>Rule 510-8-.01</td></tr>
<tr><td><strong>Ethics CE Requirement</strong></td><td><strong>6 hours</strong> in professional ethics (Area I, live/synchronous)</td><td>Rule 510-8-.01</td></tr>
<tr><td><strong>Area I CE (Live/Interactive)</strong></td><td><strong>Minimum 20 hours</strong> required (no maximum; all 40 may be Area I)</td><td>Rule 510-8-.02</td></tr>
<tr><td><strong>Area II CE (Self-Study/Courses)</strong></td><td><strong>Maximum 16 hours</strong> permitted per biennium</td><td>Rule 510-8-.02</td></tr>
<tr><td><strong>Academic Coursework CE</strong></td><td>10 hrs per semester course (max 20 hrs per biennium)</td><td>Rule 510-8-.02</td></tr>
<tr><td><strong>Peer-Reviewed Authorship CE</strong></td><td>10 hrs for 1st or 2nd author of peer-reviewed article</td><td>Rule 510-8-.02</td></tr>
<tr><td><strong>First-Time Workshop Presentation</strong></td><td>1 hr CE per hour taught (max 6 hrs per presentation)</td><td>Rule 510-8-.02</td></tr>
<tr><td><strong>Pre-Doctoral Internship</strong></td><td>Minimum <strong>1,500 hours</strong> in an organized training program</td><td>Rule 510-2-.04</td></tr>
<tr><td><strong>Post-Doctoral SWE</strong></td><td>Minimum <strong>1,500 hours</strong> (or 2,000 hrs if prior to deg conferral)</td><td>Rule 510-2-.05</td></tr>
<tr><td><strong>Max Supervisees</strong></td><td>Maximum <strong>3 supervisees</strong> concurrently without prior Board approval</td><td>Rule 510-5-.06</td></tr>
<tr><td><strong>License Expiration & Late Period</strong></td><td>Dec 31 of even years; 31-day late penalty period (Jan 1–31)</td><td>Rule 510-7-.01</td></tr>
<tr><td><strong>Reinstatement After Lapse</strong></td><td>Formal application, fees, and 40 CE hours within past 2 years</td><td>Rule 510-7-.03</td></tr>
</tbody>
</table>

<h2>2. Mandatory Reporting Overrides & Emergency Commitment</h2>
<table>
<thead><tr><th>Category</th><th>Legal Rule & Action Required</th><th>Statute</th></tr></thead>
<tbody>
<tr><td><strong>Child Abuse Reporting</strong></td><td>Mandatory reporting <strong>immediately</strong>, and in no case later than <strong>24 hours</strong> after forming suspicion. Report to DFCS or local law enforcement/prosecutor.</td><td><strong>O.C.G.A. § 19-7-5</strong></td></tr>
<tr><td><strong>Child Abuse Privilege</strong></td><td>Psychologist-client privilege is <strong>abrogated</strong>; cannot shield child abuse.</td><td>O.C.G.A. § 19-7-5(f)</td></tr>
<tr><td><strong>Child Abuse Penalty</strong></td><td>Knowing and willful failure to report is a <strong>misdemeanor</strong>.</td><td>O.C.G.A. § 19-7-5(h)</td></tr>
<tr><td><strong>Child Abuse Immunity</strong></td><td>Broad <strong>good-faith immunity</strong> from civil and criminal liability.</td><td>O.C.G.A. § 19-7-5(f)</td></tr>
<tr><td><strong>Elder / Disabled Abuse</strong></td><td>Mandatory reporting of abuse, neglect, or exploitation to Adult Protective Services (DHS) or police. Law enforcement must forward report within 24 hrs. Privilege abrogated.</td><td><strong>O.C.G.A. § 30-5-4</strong></td></tr>
<tr><td><strong>Involuntary Exam (Form 1013)</strong></td><td>Licensed psychologists have statutory authority to execute Form 1013 certificate upon determining imminent danger or grave disability.</td><td><strong>O.C.G.A. § 37-3-41</strong></td></tr>
<tr><td><strong>Peace Officer 1013 Execution</strong></td><td>Peace officers must take individual into custody within <strong>72 hours</strong> of certificate execution and deliver to emergency receiving facility.</td><td>O.C.G.A. § 37-3-41(a)</td></tr>
</tbody>
</table>

<div class="page-break"></div>

<h2>3. Confidentiality, Privilege & Prohibited Relationships</h2>
<table>
<thead><tr><th>Subject</th><th>Statutory Standard</th><th>Authority</th></tr></thead>
<tbody>
<tr><td><strong>Confidential Communications</strong></td><td>Communications between licensed psychologist and client are placed on the <strong>identical legal basis as attorney-client privilege</strong>.</td><td><strong>O.C.G.A. § 43-39-16</strong>; § 24-5-501</td></tr>
<tr><td><strong>Sexual Misconduct (1st Degree)</strong></td><td>Sexual intercourse, cunnilingus, fellatio, or anilingus with a client/patient: <strong>Felony (1 to 25 years imprisonment, up to $100,000 fine)</strong>.</td><td><strong>O.C.G.A. § 16-6-5.1</strong></td></tr>
<tr><td><strong>Sexual Misconduct (2nd Degree)</strong></td><td>Any other sexual contact with a client/patient: <strong>Misdemeanor of a high and aggravated nature</strong>.</td><td>O.C.G.A. § 16-6-5.1</td></tr>
<tr><td><strong>Defense of Consent</strong></td><td><strong>Consent of the victim is NOT a defense</strong> to prosecution for psychotherapist sexual misconduct under Georgia law.</td><td>O.C.G.A. § 16-6-5.1(b)</td></tr>
<tr><td><strong>Former Client Sexual Contact</strong></td><td>Prohibited for at least <strong>2 years</strong> following cessation of professional services under APA Ethics Code (Standard 10.08).</td><td>Rule 510-4-.02</td></tr>
</tbody>
</table>

<h2>4. Recordkeeping, Practice Limits & Disciplinary Penalties</h2>
<table>
<thead><tr><th>Topic</th><th>Legal Rule</th><th>Authority</th></tr></thead>
<tbody>
<tr><td><strong>Adult Record Retention</strong></td><td>Minimum <strong>7 years</strong> following date of last clinical service.</td><td>APA 6.01; Rule 510-4</td></tr>
<tr><td><strong>Minor Record Retention</strong></td><td>Minimum <strong>7 years past the age of majority</strong> (age 25 total).</td><td>APA 6.01; Rule 510-4</td></tr>
<tr><td><strong>Withholding Emergency Records</strong></td><td><strong>Prohibited</strong>: Records needed for emergency treatment cannot be withheld solely for nonpayment of fees.</td><td>APA Standard 6.03</td></tr>
<tr><td><strong>Bartering</strong></td><td>Permissible <strong>only if not clinically contraindicated</strong> and not exploitative.</td><td>APA Standard 6.05</td></tr>
<tr><td><strong>Test Data vs. Test Materials</strong></td><td>Test data (raw scores, answers) releasable with client consent; Test materials (manuals, test booklets) protected to preserve test security.</td><td>APA Standards 9.04, 9.11</td></tr>
<tr><td><strong>Out-of-State Practice</strong></td><td>Non-resident licensed psychologists may practice in Georgia up to <strong>30 days per calendar year</strong> with Board notification/approval.</td><td>O.C.G.A. § 43-39-7(8)</td></tr>
<tr><td><strong>PSYPACT Practice</strong></td><td>Unlimited telepsychology under E.Passport; up to 30 days temporary in-person practice under Interjurisdictional Practice Certificate (IPC).</td><td>O.C.G.A. § 43-39-20</td></tr>
<tr><td><strong>Board Civil Fines</strong></td><td>Maximum civil fine not to exceed <strong>$500.00 per violation</strong>.</td><td>O.C.G.A. § 43-1-19(d)(7)</td></tr>
<tr><td><strong>Unlicensed Practice Penalty</strong></td><td>Criminal misdemeanor: <strong>$100 to $1,000 fine and/or up to 12 months jail</strong>.</td><td>O.C.G.A. § 43-39-17</td></tr>
<tr><td><strong>Appeal of Board Decision</strong></td><td>Appeal must be filed in <strong>Superior Court of Fulton County</strong> under the Georgia Administrative Procedure Act ("any evidence" standard).</td><td>O.C.G.A. § 43-39-13; § 50-13-19</td></tr>
</tbody>
</table>
</body>
</html>
"""
    html_path.write_text(html_body, encoding="utf-8")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_build_assets.py::test_generate_cheat_sheet -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add gamb_exam/build_assets.py tests/test_build_assets.py
git commit -m "feat(assets): implement PDF compiler and statutory cheat sheet generator"
```

---

### Task 2: Full 435-Question Domain Compendium (Booklet & Back-of-Book Key)

**Files:**
- Modify: `gamb_exam/build_assets.py`
- Modify: `tests/test_build_assets.py`
- Output: `pdfs/GAMB_435_Question_Compendium.pdf`
- Output: `docs/study_materials/compendium_questions.md`
- Output: `docs/study_materials/compendium_key.md`

- [ ] **Step 1: Write failing test for compendium generation**

Add to `tests/test_build_assets.py`:
```python
from gamb_exam.build_assets import generate_compendium

def test_generate_compendium(tmp_path: Path):
    q_md = tmp_path / "compendium_questions.md"
    k_md = tmp_path / "compendium_key.md"
    html_path = tmp_path / "compendium.html"
    pdf_path = tmp_path / "compendium.pdf"

    generate_compendium(q_md=q_md, k_md=k_md, html_path=html_path)

    assert q_md.exists()
    assert k_md.exists()
    assert html_path.exists()

    q_text = q_md.read_text(encoding="utf-8")
    assert "435-Question Self-Study Compendium" in q_text
    assert "Part I: Question Bank by Domain" in q_text
    assert "Q1." in q_text
    assert "Q435." in q_text
    # Questions section must NOT reveal the correct option
    assert "Correct Option:" not in q_text

    k_text = k_md.read_text(encoding="utf-8")
    assert "Part II: Annotated Answer Key" in k_text
    assert "Q1" in k_text
    assert "Q435" in k_text

    # Test PDF compilation
    compile_html_to_pdf(html_path, pdf_path)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 100000  # Substantial multi-page PDF
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_build_assets.py::test_generate_compendium -v`  
Expected: FAIL (`ImportError: cannot import name 'generate_compendium'`).

- [ ] **Step 3: Implement `generate_compendium` in `gamb_exam/build_assets.py`**

Add `generate_compendium` to `gamb_exam/build_assets.py`:
- Loads `gamb_exam/question_pool.json`.
- Sorts items by domain in official order:
  1. `prof-relationships` (73)
  2. `licensure` (185)
  3. `competence` (104)
  4. `assessment` (30)
  5. `privacy` (22)
  6. `recordkeeping` (21)
- Generates `docs/study_materials/compendium_questions.md`: Part I only, stems and options A–D, grouped by domain with domain introductions.
- Generates `docs/study_materials/compendium_key.md`: Part II only, indexed by item ID, with Domain, Key, Primary Citation, and Explanation.
- Generates `compendium.html` combining Part I, a clear divider page (`page-break`), and Part II with clean CSS styling.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_build_assets.py::test_generate_compendium -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add gamb_exam/build_assets.py tests/test_build_assets.py
git commit -m "feat(assets): implement 435-question domain compendium generator and key"
```

---

### Task 3: Practice Exam Booklets Forms A, B, and C

**Files:**
- Modify: `gamb_exam/build_assets.py`
- Modify: `tests/test_build_assets.py`
- Output: `pdfs/GAMB_Practice_Exam_Form_A.pdf`
- Output: `pdfs/GAMB_Practice_Exam_Form_B.pdf`
- Output: `pdfs/GAMB_Practice_Exam_Form_C.pdf`
- Output: `docs/study_materials/practice_exam_form_a.md`, `form_b.md`, `form_c.md`

- [ ] **Step 1: Write failing test for practice exam forms generation**

Add to `tests/test_build_assets.py`:
```python
from gamb_exam.build_assets import generate_practice_forms

def test_generate_practice_forms(tmp_path: Path):
    forms = generate_practice_forms(output_dir=tmp_path)
    assert len(forms) == 3
    for letter, data in forms.items():
        assert letter in ["A", "B", "C"]
        assert len(data["questions"]) == 50
        # Check quota
        domain_counts = {}
        for q in data["questions"]:
            domain_counts[q["domain"]] = domain_counts.get(q["domain"], 0) + 1
        assert domain_counts == {
            "prof-relationships": 14,
            "licensure": 13,
            "competence": 9,
            "assessment": 6,
            "privacy": 5,
            "recordkeeping": 3,
        }
        # Check files created
        assert (tmp_path / f"practice_exam_form_{letter.lower()}.md").exists()
        pdf_path = tmp_path / f"GAMB_Practice_Exam_Form_{letter}.pdf"
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 30000

    # Ensure Forms A, B, and C have distinct question selections
    ids_a = {q["id"] for q in forms["A"]["questions"]}
    ids_b = {q["id"] for q in forms["B"]["questions"]}
    ids_c = {q["id"] for q in forms["C"]["questions"]}
    assert ids_a != ids_b
    assert ids_b != ids_c
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_build_assets.py::test_generate_practice_forms -v`  
Expected: FAIL (`ImportError: cannot import name 'generate_practice_forms'`).

- [ ] **Step 3: Implement `generate_practice_forms` in `gamb_exam/build_assets.py`**

In `gamb_exam/build_assets.py`:
- Use seeds 101 (Form A), 202 (Form B), 303 (Form C).
- Ingest `gamb_exam/question_pool.json`, group by domain, sample exact quotas with seeded `random.Random(seed)`.
- Generate for each form:
  - Instructions cover: 60-minute time limit, 50 questions, 38/50 (76%) pass cutoff, scoring sheet.
  - Section 1: Questions 1 to 50 with options A–D (no answers shown).
  - Section 2: Self-Scoring Bubble Sheet grid.
  - Section 3: Answer Key & Detailed Legal Citations in back.
- Compile to vector PDF using `compile_html_to_pdf`.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_build_assets.py::test_generate_practice_forms -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add gamb_exam/build_assets.py tests/test_build_assets.py
git commit -m "feat(assets): implement practice exam forms A, B, and C generation"
```

---

### Task 4: Zero-Install Standalone Web Quizzer (`web/index.html`)

**Files:**
- Modify: `gamb_exam/build_assets.py`
- Modify: `tests/test_build_assets.py`
- Output: `web/index.html`

- [ ] **Step 1: Write failing test for web quizzer compilation**

Add to `tests/test_build_assets.py`:
```python
from gamb_exam.build_assets import generate_web_quizzer

def test_generate_web_quizzer(tmp_path: Path):
    web_file = tmp_path / "index.html"
    generate_web_quizzer(output_path=web_file)

    assert web_file.exists()
    content = web_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "Georgia Psychology Jurisprudence Examination" in content
    assert "PSI Exam Simulation" in content
    assert "Domain Study Drill" in content
    assert "Missed Questions" in content
    assert "const QUESTION_BANK =" in content
    # Check that all 435 questions are serialized
    assert '"id": 1' in content
    assert '"id": 435' in content
    assert "localStorage" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_build_assets.py::test_generate_web_quizzer -v`  
Expected: FAIL (`ImportError: cannot import name 'generate_web_quizzer'`).

- [ ] **Step 3: Implement `generate_web_quizzer` in `gamb_exam/build_assets.py`**

In `gamb_exam/build_assets.py`:
- Ingest `gamb_exam/question_pool.json`.
- Render a self-contained, zero-dependency HTML5 application with:
  - **Embedded JSON**: `const QUESTION_BANK = [...]` containing all 435 questions with `id`, `domain`, `subtopic`, `source_citation`, `question_text`, `options`, `correct_option`, `explanation`.
  - **CSS Styling**: High-contrast, clean typography, responsive on mobile and desktop, card-based layout, instant green/red answer highlighting, modal/jump grid, dark/light toggle.
  - **JS Engine**:
    - Mode 1: PSI Timed Simulation (50 questions, 60-minute countdown timer, domain quotas 14/13/9/6/5/3, question flag toggle `[F]`, jump grid, 38/50 76% score report, review mode).
    - Mode 2: Domain Study Drill (filter by any of the 6 domains, instant reveal with statutory citations & explanations on click).
    - Mode 3: Missed Questions Drill (reads from browser `localStorage` to practice previously missed questions).
    - Desktop keyboard shortcuts (`A`, `B`, `C`, `D`, `N`, `P`, `F`).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_build_assets.py::test_generate_web_quizzer -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add gamb_exam/build_assets.py tests/test_build_assets.py
git commit -m "feat(assets): implement zero-install standalone web quizzer"
```

---

### Task 5: CLI Subcommand Integration (`gamb-exam build-assets`)

**Files:**
- Modify: `gamb_exam/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing test for `build-assets` CLI command**

Add to `tests/test_cli.py`:
```python
def test_build_assets_cli_help(capsys):
    from gamb_exam.cli import main
    exit_code = main(["build-assets", "--help"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "build-assets" in captured.out
    assert "--output-dir" in captured.out

def test_build_assets_cli_execution(tmp_path, monkeypatch):
    from gamb_exam.cli import main
    exit_code = main(["build-assets", "--output-dir", str(tmp_path)])
    assert exit_code == 0
    assert (tmp_path / "pdfs" / "GAMB_Statutory_Cheat_Sheet.pdf").exists()
    assert (tmp_path / "pdfs" / "GAMB_435_Question_Compendium.pdf").exists()
    assert (tmp_path / "web" / "index.html").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_build_assets_cli_help -v`  
Expected: FAIL (`unrecognized arguments: build-assets`).

- [ ] **Step 3: Integrate `build-assets` into `gamb_exam/cli.py`**

In `gamb_exam/cli.py`:
- Add `handle_build_assets(args: argparse.Namespace) -> int`:
  - Calls `build_all_assets(output_dir=args.output_dir)`.
  - Prints rich status messages with paths to generated PDFs, Markdown sources, and `web/index.html`.
- Add parser in `create_parser()`:
  - `build_parser = subparsers.add_parser("build-assets", help="Build all consumer study products (PDFs, Markdown, Web Quizzer)")`
  - `--output-dir` (default: repository root).

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py::test_build_assets_cli_help tests/test_cli.py::test_build_assets_cli_execution -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add gamb_exam/cli.py tests/test_cli.py
git commit -m "feat(cli): add build-assets subcommand"
```

---

### Task 6: Full Asset Generation, Verification & README Overhaul

**Files:**
- Modify: `README.md`
- Generate: `pdfs/*.pdf`, `web/index.html`, `docs/study_materials/*.md`

- [ ] **Step 1: Execute full asset build in workspace**

Run:
```bash
uv run gamb-exam build-assets
```
Expected: All 5 PDF files generated in `pdfs/`, `web/index.html` generated in `web/`, Markdown study packets in `docs/study_materials/`.

- [ ] **Step 2: Verify all assets**

Verify:
```bash
ls -lh pdfs/ web/ docs/study_materials/
```
Ensure all 5 PDFs are non-empty (>10KB) and `web/index.html` is intact.

- [ ] **Step 3: Update `README.md` with Consumer Products Section**

Add a prominent top-level **"📦 Study Products & Downloads (No Installation Required)"** section immediately below the disclaimer:
- Direct links to `pdfs/GAMB_Statutory_Cheat_Sheet.pdf`.
- Direct links to `pdfs/GAMB_435_Question_Compendium.pdf`.
- Direct links to `pdfs/GAMB_Practice_Exam_Form_A.pdf`, `Form_B.pdf`, `Form_C.pdf`.
- Instructions for downloading/opening `web/index.html` offline on computer/phone, and deploying to personal website.
- Clear guide for Anki flashcard deck (`anki/gamb_deck.tsv`).
- Terminal simulator instructions for technical users.

- [ ] **Step 4: Run full test suite**

Run:
```bash
uv run pytest
```
Expected: 100% PASS across all unit, cli, db, generator, pool, seed, tui, and build_assets tests.

- [ ] **Step 5: Commit and push to GitHub origin/master**

```bash
git add pdfs/ web/ docs/ README.md
git commit -m "feat(products): package consumer PDFs, offline web quizzer, and update README"
git push origin master
```
