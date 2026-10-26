"""Asset generation pipeline for Georgia Psychology Jurisprudence Examination study products."""

from __future__ import annotations

import html
import json
import random
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from gamb_exam.generator import DOMAIN_DISPLAY_NAMES, DOMAIN_QUOTAS, LEGAL_DISCLAIMER
from gamb_exam.seed import (
    QUESTION_POOL_DATE,
    QUESTION_POOL_VERSION,
)

POOL_VERSION: str = QUESTION_POOL_VERSION
POOL_DATE: str = QUESTION_POOL_DATE

OFFICIAL_DOMAIN_ORDER: list[str] = [
    "prof-relationships",
    "licensure",
    "competence",
    "assessment",
    "privacy",
    "recordkeeping",
]

DOMAIN_DESCRIPTIONS: dict[str, str] = {
    "prof-relationships": "Rules governing dual and multiple relationships, sexual misconduct (O.C.G.A. § 16-6-5.1), conflicts of interest, supervisory responsibilities (Rule 510-5-.06), and interprofessional relationships.",
    "licensure": "Statutory qualifications for licensure, doctoral training, pre-doctoral internships, post-doctoral supervised work experience, examination requirements, license renewal, and continuing education (Rules 510-2, 510-7, 510-8).",
    "competence": "Scope of practice, boundaries of competence, maintenance of expertise, impairment and professional consultation, telepsychology standards, and emergency interventions (Rule 510-4, O.C.G.A. § 37-3-41).",
    "assessment": "Selection, administration, scoring, and interpretation of psychological assessment instruments, test security, release of test data versus test materials, and forensic assessment standards (Rule 510-4, APA Standards 9.04, 9.11).",
    "privacy": "Confidential communications, psychologist-client privilege (O.C.G.A. § 43-39-16), statutory mandatory reporting overrides for child abuse (O.C.G.A. § 19-7-5) and elder/vulnerable adult abuse (O.C.G.A. § 30-5-4).",
    "recordkeeping": "Maintenance, retention, and disposition of psychological records (7-year retention rule for adults; 7 years post-majority for minors), fee arrangements, billing practices, and financial disclosures (Rule 510-4, APA 6.01, 6.03).",
}

PRINT_PAGE_RULE = f"""
@page {{
    size: letter;
    margin: 0.75in 0.75in 0.85in 0.75in;
    @top-left {{
        content: "GAMB Study Guide";
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 8pt;
        color: #718096;
    }}
    @top-right {{
        content: "Question Pool v{POOL_VERSION} ({POOL_DATE})";
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 8pt;
        color: #718096;
    }}
    @bottom-center {{
        content: "Page " counter(page) " of " counter(pages);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 8pt;
        color: #718096;
    }}
}}
"""

PRINT_CSS = PRINT_PAGE_RULE + """

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
    if not html_path.exists():
        raise FileNotFoundError(f"HTML source file not found: {html_path}")

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    weasyprint_bin = shutil.which("weasyprint")
    if weasyprint_bin:
        cmd = [weasyprint_bin, str(html_path), str(pdf_path)]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0:
            raise RuntimeError(f"WeasyPrint failed ({res.returncode}): {res.stderr.strip()}")
    else:
        try:
            import weasyprint
        except ImportError as err:
            raise RuntimeError(
                "Neither weasyprint CLI binary nor weasyprint Python package is available"
            ) from err

        try:
            weasyprint.HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        except Exception as err:
            raise RuntimeError(f"WeasyPrint rendering failed: {err}") from err


def generate_cheat_sheet(md_path: Path, html_path: Path) -> None:
    """Generate the high-yield Statutory Quick-Reference Cheat Sheet in Markdown and HTML."""
    md_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)

    md_content = f"""# Georgia Psychology Jurisprudence Examination (GAMB)
## High-Yield Statutory Quick-Reference Cheat Sheet
> **Question Pool:** Version {POOL_VERSION} (Date: {POOL_DATE})

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

### 4. Recordkeeping, Practice Limits & Disciplinary Penalties

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
<div class="badge" style="background-color: #ebf8ff; color: #2b6cb0; margin-left: 4pt;">QUESTION POOL v{POOL_VERSION} ({POOL_DATE})</div>
<div class="meta-info" style="font-size: 8.5pt; color: #4a5568; margin-top: 4pt; margin-bottom: 8pt;">
<strong>Question Pool:</strong> Version {POOL_VERSION} &bull; <strong>Release Date:</strong> {POOL_DATE}
</div>
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


def generate_compendium(
    q_md: Path | None = None,
    k_md: Path | None = None,
    html_path: Path | None = None,
    pool_path: Path | None = None,
) -> None:
    """Generate the full 435-question domain compendium booklet and back-of-book key."""
    repo_root = Path(__file__).resolve().parent.parent
    q_md = q_md or repo_root / "docs" / "study_materials" / "compendium_questions.md"
    k_md = k_md or repo_root / "docs" / "study_materials" / "compendium_key.md"
    html_path = html_path or repo_root / "docs" / "study_materials" / "compendium.html"
    pool_path = pool_path or repo_root / "gamb_exam" / "question_pool.json"

    q_md.parent.mkdir(parents=True, exist_ok=True)
    k_md.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)

    with pool_path.open("r", encoding="utf-8") as f:
        pool_data: list[dict] = json.load(f)

    # Group questions by official domain
    questions_by_domain: dict[str, list[dict]] = {d: [] for d in OFFICIAL_DOMAIN_ORDER}
    for item in pool_data:
        domain = item.get("domain", "")
        if domain in questions_by_domain:
            questions_by_domain[domain].append(item)
        else:
            questions_by_domain.setdefault(domain, []).append(item)

    # Deterministic sorting within each domain by item id
    for domain_items in questions_by_domain.values():
        domain_items.sort(key=lambda x: x.get("id", 0))

    extra_domains = [d for d in questions_by_domain if d not in OFFICIAL_DOMAIN_ORDER]
    all_domains = list(OFFICIAL_DOMAIN_ORDER) + extra_domains

    # Sequential numbering across the entire compendium (1..N)
    ordered_questions: list[tuple[int, dict]] = []
    ordered_by_domain: dict[str, list[tuple[int, dict]]] = {d: [] for d in all_domains}
    q_counter = 1
    for domain in all_domains:
        for q in questions_by_domain.get(domain, []):
            item = (q_counter, q)
            ordered_questions.append(item)
            ordered_by_domain[domain].append(item)
            q_counter += 1

    total_qs = len(ordered_questions)

    # 1. Build Part I Markdown (compendium_questions.md)
    md_q_lines: list[str] = [
        "# Georgia Psychology Jurisprudence Examination (GAMB)",
        f"## {total_qs}-Question Self-Study Compendium",
        "## Part I: Question Bank by Domain",
        f"> **Question Pool Version:** {POOL_VERSION} (Release Date: {POOL_DATE})",
        "",
        LEGAL_DISCLAIMER,
        "",
        "---",
        "",
    ]

    for d_idx, domain in enumerate(all_domains, 1):
        domain_title = DOMAIN_DISPLAY_NAMES.get(domain, domain)
        domain_desc = DOMAIN_DESCRIPTIONS.get(domain, "")
        domain_qs = ordered_by_domain.get(domain, [])
        md_q_lines.append(f"## Domain {d_idx}: {domain_title} ({len(domain_qs)} Questions)\n")
        if domain_desc:
            md_q_lines.append(f"*{domain_desc}*\n")
        for q_num, q in domain_qs:
            q_text = q.get("question_text", "").strip()
            options = q.get("options", {})
            md_q_lines.append(f"### Q{q_num}. {q_text}\n")
            for opt_key in ["A", "B", "C", "D"]:
                opt_val = options.get(opt_key, "").strip()
                md_q_lines.append(f"- **{opt_key})** {opt_val}")
            md_q_lines.append("")

    q_md.write_text("\n".join(md_q_lines), encoding="utf-8")

    # 2. Build Part II Markdown (compendium_key.md)
    md_k_lines: list[str] = [
        "# Georgia Psychology Jurisprudence Examination (GAMB)",
        f"## {total_qs}-Question Self-Study Compendium",
        "## Part II: Annotated Answer Key",
        f"> **Question Pool Version:** {POOL_VERSION} (Release Date: {POOL_DATE})",
        "",
        LEGAL_DISCLAIMER,
        "",
        "---",
        "",
    ]

    for q_num, q in ordered_questions:
        domain = q.get("domain", "")
        domain_title = DOMAIN_DISPLAY_NAMES.get(domain, domain)
        md_k_lines.append(f"### Q{q_num} (Pool Item #{q.get('id', '')})")
        md_k_lines.append(f"- **Domain:** {domain_title}")
        md_k_lines.append(f"- **Correct Option:** {q.get('correct_option', '').strip()}")
        md_k_lines.append(f"- **Source Citation:** {q.get('source_citation', '').strip()}")
        md_k_lines.append(f"- **Explanation:** {q.get('explanation', '').strip()}")
        md_k_lines.append("")

    k_md.write_text("\n".join(md_k_lines), encoding="utf-8")

    # 3. Build Combined HTML (compendium.html)
    html_parts: list[str] = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        f"<title>GAMB {total_qs}-Question Domain Compendium</title>",
        f"<style>\n{PRINT_CSS}\n</style>",
        "</head>",
        "<body>",
        "<h1>Georgia Psychology Jurisprudence Examination (GAMB)</h1>",
        f'<div class="badge">{total_qs}-QUESTION SELF-STUDY COMPENDIUM</div>',
        f'<div class="badge" style="background-color: #ebf8ff; color: #2b6cb0; margin-left: 4pt;">QUESTION POOL v{POOL_VERSION} &bull; {POOL_DATE}</div>',
        f'<div style="font-size: 8.5pt; color: #4a5568; margin-top: 4pt; margin-bottom: 6pt;"><strong>Question Pool:</strong> Version {POOL_VERSION} &bull; <strong>Release Date:</strong> {POOL_DATE} &bull; <strong>Total Questions:</strong> {total_qs}</div>',
        "<h2>Part I: Question Bank by Domain</h2>",
        '<div class="disclaimer">',
        "<strong>LEGAL &amp; REGULATORY DISCLAIMER:</strong> This compendium is an independently authored study aid and is NOT official examination material from the Georgia State Board of Examiners of Psychologists or PSI Services LLC. Verified against O.C.G.A. and Board Rules Chapter 510.",
        "</div>",
    ]

    for d_idx, domain in enumerate(all_domains, 1):
        domain_title = DOMAIN_DISPLAY_NAMES.get(domain, domain)
        domain_desc = DOMAIN_DESCRIPTIONS.get(domain, "")
        domain_qs = ordered_by_domain.get(domain, [])
        if d_idx > 1:
            html_parts.append('<div class="page-break"></div>')
        html_parts.append(f"<h2>Domain {d_idx}: {html.escape(domain_title)} ({len(domain_qs)} Questions)</h2>")
        if domain_desc:
            html_parts.append(f'<p style="color: #4a5568; font-style: italic; margin-bottom: 12pt;">{html.escape(domain_desc)}</p>')
        for q_num, q in domain_qs:
            q_text = q.get("question_text", "").strip()
            options = q.get("options", {})
            html_parts.append('<div class="question-block">')
            html_parts.append(f'<div class="question-text">Q{q_num}. {html.escape(q_text)}</div>')
            for opt_key in ["A", "B", "C", "D"]:
                opt_val = options.get(opt_key, "").strip()
                html_parts.append(f'<div class="option"><strong>{opt_key}.</strong> {html.escape(opt_val)}</div>')
            html_parts.append("</div>")

    # Section divider page
    html_parts.extend([
        '<div class="page-break"></div>',
        '<div style="text-align: center; padding-top: 220pt;">',
        '<h1 style="border-bottom: none; font-size: 24pt; color: #1a365d;">Part II: Annotated Answer Key</h1>',
        f'<div class="badge" style="font-size: 10pt; margin-top: 8pt; padding: 3pt 8pt;">QUESTIONS 1 &ndash; {total_qs}</div>',
        f'<div class="badge" style="background-color: #ebf8ff; color: #2b6cb0; font-size: 10pt; margin-top: 8pt; padding: 3pt 8pt; margin-left: 4pt;">QUESTION POOL v{POOL_VERSION} ({POOL_DATE})</div>',
        '<p style="font-size: 11pt; color: #4a5568; margin-top: 14pt;">Official Legal Authorities, Source Citations, and Explanations</p>',
        "</div>",
        '<div class="page-break"></div>',
        "<h2>Part II: Annotated Answer Key</h2>",
        '<div class="disclaimer">',
        "<strong>INSTRUCTIONS:</strong> Verify answers and review relevant O.C.G.A. statutory sections and Board Rules Chapter 510 citations for complete legal rationales.",
        "</div>",
    ])

    for q_num, q in ordered_questions:
        domain = q.get("domain", "")
        domain_title = DOMAIN_DISPLAY_NAMES.get(domain, domain)
        correct_opt = q.get("correct_option", "").strip()
        citation = q.get("source_citation", "").strip()
        explanation = q.get("explanation", "").strip()
        html_parts.append('<div class="key-block">')
        html_parts.append(
            f'<div style="font-weight: bold; font-size: 10pt; color: #2c5282; margin-bottom: 2pt;">'
            f'Q{q_num} &mdash; <span class="badge">{html.escape(domain_title)}</span> &mdash; '
            f'Correct Option: <strong style="color: #2b6cb0;">{html.escape(correct_opt)}</strong>'
            f'</div>'
        )
        if citation:
            html_parts.append(
                f'<div style="font-size: 8.5pt; color: #4a5568; margin-bottom: 2pt;">'
                f'<strong>Citation:</strong> <em>{html.escape(citation)}</em>'
                f'</div>'
            )
        if explanation:
            html_parts.append(
                f'<div style="font-size: 9pt; color: #2d3748;">'
                f'<strong>Explanation:</strong> {html.escape(explanation)}'
                f'</div>'
            )
        html_parts.append("</div>")

    html_parts.extend(["</body>", "</html>"])
    html_path.write_text("\n".join(html_parts), encoding="utf-8")


def generate_practice_forms(
    output_dir: Path | str | None = None,
    md_dir: Path | str | None = None,
    pdf_dir: Path | str | None = None,
    pool_path: Path | str | None = None,
) -> dict[str, dict[str, Any]]:
    """Generate Practice Examination Booklets Forms A, B, and C with seeded sampling.

    Each booklet contains:
    - Cover page with official instructions, 60-min time limit, and passing standards
    - Section 1: 50 multiple-choice questions (unmarked options A-D)
    - Section 2: Self-Scoring Bubble Sheet grid / table
    - Section 3: Answer Key, Domain Diagnostic Worksheet & Detailed Legal Citations

    Args:
        output_dir: Target directory for both markdown and PDF outputs (useful for tests).
        md_dir: Optional specific directory for markdown booklets.
        pdf_dir: Optional specific directory for PDF booklets.
        pool_path: Optional path to question pool JSON file.

    Returns:
        Dict mapping form letters ("A", "B", "C") to dict containing "questions", "md_path", "pdf_path".
    """
    repo_root = Path(__file__).resolve().parent.parent
    if output_dir is not None:
        target_md_dir = Path(output_dir)
        target_pdf_dir = Path(output_dir)
    else:
        target_md_dir = Path(md_dir) if md_dir is not None else repo_root / "docs" / "study_materials"
        target_pdf_dir = Path(pdf_dir) if pdf_dir is not None else repo_root / "pdfs"

    target_md_dir.mkdir(parents=True, exist_ok=True)
    target_pdf_dir.mkdir(parents=True, exist_ok=True)

    pool_file = Path(pool_path) if pool_path is not None else repo_root / "gamb_exam" / "question_pool.json"
    with pool_file.open("r", encoding="utf-8") as f:
        pool_data: list[dict[str, Any]] = json.load(f)

    # Group questions by official domain
    questions_by_domain: dict[str, list[dict[str, Any]]] = {d: [] for d in OFFICIAL_DOMAIN_ORDER}
    for item in pool_data:
        domain = item.get("domain", "")
        if domain in questions_by_domain:
            questions_by_domain[domain].append(item)
        else:
            questions_by_domain.setdefault(domain, []).append(item)

    # Deterministic sorting within each domain by item id
    for domain_items in questions_by_domain.values():
        domain_items.sort(key=lambda x: x.get("id", 0))

    form_configs: list[tuple[str, int]] = [
        ("A", 101),
        ("B", 202),
        ("C", 303),
    ]

    forms_result: dict[str, dict[str, Any]] = {}

    for form_letter, seed in form_configs:
        rng = random.Random(seed)
        sampled_qs: list[dict[str, Any]] = []

        for domain in OFFICIAL_DOMAIN_ORDER:
            quota = DOMAIN_QUOTAS.get(domain, 0)
            candidates = questions_by_domain.get(domain, [])
            if len(candidates) < quota:
                raise ValueError(
                    f"Insufficient questions in domain '{domain}': requested {quota}, found {len(candidates)}"
                )
            sampled_qs.extend(rng.sample(candidates, quota))

        # Shuffle the 50 sampled questions across the exam
        rng.shuffle(sampled_qs)

        # Shuffle options A-D for each question, preserving correct answer tracking
        form_questions: list[dict[str, Any]] = []
        for q in sampled_qs:
            orig_options = q.get("options", {})
            orig_correct = q.get("correct_option", "").strip().upper()
            opt_a = (orig_options.get("A", "") or q.get("option_a", "")).strip()
            opt_b = (orig_options.get("B", "") or q.get("option_b", "")).strip()
            opt_c = (orig_options.get("C", "") or q.get("option_c", "")).strip()
            opt_d = (orig_options.get("D", "") or q.get("option_d", "")).strip()
            pairs = [
                (opt_a, orig_correct == "A"),
                (opt_b, orig_correct == "B"),
                (opt_c, orig_correct == "C"),
                (opt_d, orig_correct == "D"),
            ]
            rng.shuffle(pairs)
            new_options: dict[str, str] = {}
            new_correct = ""
            for idx, (text, is_corr) in enumerate(pairs):
                letter = ["A", "B", "C", "D"][idx]
                new_options[letter] = text
                if is_corr:
                    new_correct = letter

            if not new_correct:
                raise ValueError(
                    f"Question item {q.get('id')} has invalid or missing correct_option: {q.get('correct_option')}"
                )

            q_proc = dict(q)
            q_proc["options"] = new_options
            q_proc["correct_option"] = new_correct
            q_proc["option_a"] = new_options["A"]
            q_proc["option_b"] = new_options["B"]
            q_proc["option_c"] = new_options["C"]
            q_proc["option_d"] = new_options["D"]
            form_questions.append(q_proc)

        # 1. Build Markdown File
        md_file = target_md_dir / f"practice_exam_form_{form_letter.lower()}.md"
        md_lines: list[str] = [
            "# Georgia Psychology Jurisprudence Examination (GAMB)",
            f"## Practice Examination Booklet — Form {form_letter}",
            f"### 50-Question Stratified Jurisprudence Simulation (Seed {seed})",
            f"> **Question Pool Version:** {POOL_VERSION} (Release Date: {POOL_DATE})",
            "",
            LEGAL_DISCLAIMER,
            "",
            "---",
            "",
            "## Exam Instructions & Scoring Guide",
            "",
            "- **Time Limit:** 60 minutes (strict simulation conditions)",
            "- **Item Count:** 50 multiple-choice questions (A, B, C, D)",
            "- **Passing Standard:** 38 out of 50 correct (76.0%)",
            "- **Format:** Closed-book examination. Select the single best answer for each question.",
            "- **Official Domain Distribution:**",
            "  - Professional Relationships: 14 questions (28%)",
            "  - Licensure and Regulations: 13 questions (26%)",
            "  - Competence: 9 questions (18%)",
            "  - Assessment: 6 questions (12%)",
            "  - Privacy and Confidentiality: 5 questions (10%)",
            "  - Recordkeeping and Fees: 3 questions (6%)",
            "- **Booklet Structure:**",
            "  - **Section 1:** Examination Questions (Q1 – Q50)",
            "  - **Section 2:** Candidate Bubble Sheet & Scoring Grid",
            "  - **Section 3:** Answer Key, Domain Diagnostic Worksheet & Detailed Legal Citations",
            "",
            "---",
            "",
            "## Section 1: Examination Questions",
            "",
        ]

        for idx, q in enumerate(form_questions, 1):
            q_text = q.get("question_text", "").strip()
            opts = q.get("options", {})
            md_lines.append(f"### Q{idx}. {q_text}\n")
            for opt_key in ["A", "B", "C", "D"]:
                md_lines.append(f"- **{opt_key})** {opts.get(opt_key, '').strip()}")
            md_lines.append("")

        md_lines.extend([
            "---",
            "",
            "## Section 2: Candidate Bubble Sheet & Scoring Grid",
            "",
            "Record your responses below. Mark only one letter per item. After completing the exam under 60-minute timed conditions, proceed to Section 3 to score your responses.",
            "",
            "| Q# | Candidate Response | Q# | Candidate Response |",
            "|:--:|:------------------:|:--:|:------------------:|",
        ])

        for i in range(1, 26):
            md_lines.append(
                f"| {i} | [ ] A  [ ] B  [ ] C  [ ] D | {i + 25} | [ ] A  [ ] B  [ ] C  [ ] D |"
            )

        md_lines.extend([
            "",
            "### Candidate Scoring Summary",
            "",
            "| Metric | Candidate Result | Official Standard | Examination Status |",
            "|:---|:---:|:---:|:---:|",
            "| **Total Correct Items** | _____ / 50 | 38 / 50 items | [ ] PASS  [ ] FAIL |",
            "| **Passing Percentage** | _____ % | 76.0% Minimum | [ ] PASS  [ ] FAIL |",
            "",
            "---",
            "",
            "## Section 3: Answer Key & Detailed Legal Citations",
            "",
            "> [!IMPORTANT]",
            "> **STOP**: Do not review this section until you have completed all 50 questions under timed conditions.",
            "",
            "### Domain Score Diagnostic Worksheet",
            "",
            "| Domain | Code | Tested Items | Your Score | Target (>=70%) | Diagnostic Status |",
            "|:---|:---|:---:|:---:|:---:|:---:|",
            "| Professional Relationships | `prof-relationships` | 14 | / 14 | 10 / 14 (71%) | [ ] Meets Target  [ ] Needs Review |",
            "| Licensure and Regulations | `licensure` | 13 | / 13 | 9 / 13 (69%) | [ ] Meets Target  [ ] Needs Review |",
            "| Competence | `competence` | 9 | / 9 | 6 / 9 (67%) | [ ] Meets Target  [ ] Needs Review |",
            "| Assessment | `assessment` | 6 | / 6 | 4 / 6 (67%) | [ ] Meets Target  [ ] Needs Review |",
            "| Privacy and Confidentiality | `privacy` | 5 | / 5 | 4 / 5 (80%) | [ ] Meets Target  [ ] Needs Review |",
            "| Recordkeeping and Fees | `recordkeeping` | 3 | / 3 | 2 / 3 (67%) | [ ] Meets Target  [ ] Needs Review |",
            "| **Total Examination** | **All Domains** | **50** | **/ 50** | **38 / 50 (76%)** | **[ ] PASS  [ ] FAIL** |",
            "",
            "### Quick-Reference Answer Key",
            "",
            "| Q# | Domain | Correct Option | Legal Citation |",
            "|:--:|:-------|:--------------:|:---------------|",
        ])

        for idx, q in enumerate(form_questions, 1):
            domain_name = DOMAIN_DISPLAY_NAMES.get(q.get("domain", ""), q.get("domain", ""))
            clean_cite = str(q.get("source_citation", "")).replace("|", "\\|").replace("\n", " ").strip()
            md_lines.append(f"| {idx} | {domain_name} | **{q.get('correct_option', '')}** | {clean_cite} |")

        md_lines.extend([
            "",
            "### Detailed Item-by-Item Review",
            "",
        ])

        for idx, q in enumerate(form_questions, 1):
            domain_name = DOMAIN_DISPLAY_NAMES.get(q.get("domain", ""), q.get("domain", ""))
            md_lines.extend([
                f"### Q{idx} (Pool Item #{q.get('id', '')})",
                f"- **Domain:** {domain_name}",
                f"- **Correct Option:** {q.get('correct_option', '')}",
                f"- **Source Citation:** {q.get('source_citation', '').strip()}",
                f"- **Explanation:** {q.get('explanation', '').strip()}",
                "",
            ])

        md_file.write_text("\n".join(md_lines), encoding="utf-8")

        # 2. Build HTML File
        html_file = (target_pdf_dir if output_dir is not None else target_md_dir) / f"practice_exam_form_{form_letter.lower()}.html"
        pdf_file = target_pdf_dir / f"GAMB_Practice_Exam_Form_{form_letter}.pdf"

        custom_css = PRINT_CSS.replace(
            'content: "GAMB Study Guide";',
            f'content: "GAMB Practice Exam Booklet — Form {form_letter}";',
        ) + """
.bubble {
    display: inline-block;
    width: 13pt;
    height: 13pt;
    border-radius: 50%;
    border: 1pt solid #4a5568;
    text-align: center;
    line-height: 13pt;
    font-size: 7.5pt;
    font-weight: bold;
    margin: 0 1.5pt;
    color: #4a5568;
}
.bubble-grid {
    width: 100%;
    margin-top: 8pt;
    margin-bottom: 12pt;
    font-size: 8.5pt;
}
.bubble-grid td {
    padding: 3pt 6pt;
    vertical-align: middle;
}
"""

        html_parts: list[str] = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '<meta charset="utf-8">',
            f"<title>GAMB Practice Exam Booklet &mdash; Form {form_letter}</title>",
            f"<style>\n{custom_css}\n</style>",
            "</head>",
            "<body>",
            "<h1>Georgia Psychology Jurisprudence Examination (GAMB)</h1>",
            f'<div class="badge" style="font-size: 10pt; padding: 3pt 8pt; margin-bottom: 6pt;">PRACTICE EXAMINATION BOOKLET &bull; FORM {form_letter}</div>',
            f'<div class="badge" style="background-color: #ebf8ff; color: #2b6cb0; font-size: 10pt; padding: 3pt 8pt; margin-bottom: 10pt; margin-left: 4pt;">QUESTION POOL v{POOL_VERSION} ({POOL_DATE})</div>',
            '<div style="background-color: #f7fafc; border: 1pt solid #cbd5e0; border-radius: 4pt; padding: 10pt 14pt; margin-bottom: 14pt;">',
            '<h3 style="margin-top: 0; color: #1a365d;">Examination Instructions &amp; Candidate Guidelines</h3>',
            f'<p style="margin: 4pt 0;"><strong>Question Pool:</strong> Version {POOL_VERSION} (Release Date: {POOL_DATE})</p>',
            '<p style="margin: 4pt 0;"><strong>Time Limit:</strong> 60 minutes (strict simulation conditions)</p>',
            '<p style="margin: 4pt 0;"><strong>Total Items:</strong> 50 multiple-choice questions (A, B, C, D)</p>',
            '<p style="margin: 4pt 0;"><strong>Passing Standard:</strong> 38 out of 50 correct (76.0%)</p>',
            '<p style="margin: 4pt 0;"><strong>Examination Format:</strong> Closed-book examination. Select the single best answer for each question.</p>',
            '<p style="margin: 4pt 0;"><strong>Official Domain Composition:</strong></p>',
            '<ul style="margin: 4pt 0 4pt 16pt; padding: 0;">',
            '<li>Professional Relationships: 14 questions (28%)</li>',
            '<li>Licensure and Regulations: 13 questions (26%)</li>',
            '<li>Competence: 9 questions (18%)</li>',
            '<li>Assessment: 6 questions (12%)</li>',
            '<li>Privacy and Confidentiality: 5 questions (10%)</li>',
            '<li>Recordkeeping and Fees: 3 questions (6%)</li>',
            '</ul>',
            '<p style="margin: 4pt 0 0 0;"><strong>Booklet Layout:</strong> Section 1: Questions (1–50) | Section 2: Bubble Sheet | Section 3: Answer Key &amp; Explanations</p>',
            '</div>',
            '<div class="disclaimer">',
            '<strong>LEGAL &amp; REGULATORY DISCLAIMER:</strong> This practice exam is an independently authored study aid and is NOT official examination material from the Georgia State Board of Examiners of Psychologists or PSI Services LLC. Verified against O.C.G.A. Title 43, Chapter 39 and Board Rules Chapter 510.',
            '</div>',
            '<div class="page-break"></div>',
            f'<h2>Section 1: Examination Questions &mdash; Form {form_letter}</h2>',
        ]

        for idx, q in enumerate(form_questions, 1):
            q_text = q.get("question_text", "").strip()
            opts = q.get("options", {})
            html_parts.append('<div class="question-block">')
            html_parts.append(f'<div class="question-text">Q{idx}. {html.escape(q_text)}</div>')
            for opt_key in ["A", "B", "C", "D"]:
                opt_val = opts.get(opt_key, "").strip()
                html_parts.append(f'<div class="option"><strong>{opt_key}.</strong> {html.escape(opt_val)}</div>')
            html_parts.append('</div>')

        # Section 2 HTML
        html_parts.extend([
            '<div class="page-break"></div>',
            f'<h2>Section 2: Candidate Bubble Sheet &amp; Scoring Grid &mdash; Form {form_letter}</h2>',
            f'<p style="color: #4a5568; font-size: 9pt;">Record your responses by marking the circle corresponding to your selected option. Form {form_letter} &bull; Question Pool v{POOL_VERSION} ({POOL_DATE}). Upon completing all 50 items under timed conditions, proceed to Section 3.</p>',
            '<table class="bubble-grid">',
            '<thead>',
            '<tr>',
            '<th style="width: 8%; text-align: center;">Q#</th>',
            '<th style="width: 42%; text-align: center;">Candidate Response</th>',
            '<th style="width: 8%; text-align: center;">Q#</th>',
            '<th style="width: 42%; text-align: center;">Candidate Response</th>',
            '</tr>',
            '</thead>',
            '<tbody>',
        ])

        for i in range(1, 26):
            html_parts.append(
                f'<tr>'
                f'<td style="text-align: center; font-weight: bold;">{i}</td>'
                f'<td style="text-align: center;">'
                f'<span class="bubble">A</span><span class="bubble">B</span><span class="bubble">C</span><span class="bubble">D</span>'
                f'</td>'
                f'<td style="text-align: center; font-weight: bold;">{i + 25}</td>'
                f'<td style="text-align: center;">'
                f'<span class="bubble">A</span><span class="bubble">B</span><span class="bubble">C</span><span class="bubble">D</span>'
                f'</td>'
                f'</tr>'
            )

        html_parts.extend([
            '</tbody>',
            '</table>',
            '<h3>Candidate Scoring Summary</h3>',
            '<table>',
            '<thead><tr><th>Metric</th><th>Candidate Result</th><th>Official Standard</th><th>Examination Status</th></tr></thead>',
            '<tbody>',
            '<tr><td><strong>Total Correct Items</strong></td><td>_____ / 50</td><td>38 / 50 items</td><td>[ ] PASS &nbsp; [ ] FAIL</td></tr>',
            '<tr><td><strong>Passing Percentage</strong></td><td>_____ %</td><td>76.0% Minimum</td><td>[ ] PASS &nbsp; [ ] FAIL</td></tr>',
            '</tbody>',
            '</table>',
        ])

        # Section 3 HTML
        html_parts.extend([
            '<div class="page-break"></div>',
            '<div style="text-align: center; padding-top: 220pt;">',
            '<h1 style="border-bottom: none; font-size: 24pt; color: #1a365d;">Section 3: Answer Key &amp; Explanations</h1>',
            f'<div class="badge" style="font-size: 10pt; margin-top: 8pt; padding: 3pt 8pt;">FORM {form_letter} &bull; QUESTIONS 1 &ndash; 50</div>',
            f'<div class="badge" style="background-color: #ebf8ff; color: #2b6cb0; font-size: 10pt; margin-top: 8pt; padding: 3pt 8pt; margin-left: 4pt;">QUESTION POOL v{POOL_VERSION} ({POOL_DATE})</div>',
            '<p style="font-size: 11pt; color: #4a5568; margin-top: 14pt;">Official Legal Authorities, Source Citations, and Domain Diagnostic Key</p>',
            '</div>',
            '<div class="page-break"></div>',
            f'<h2>Section 3: Answer Key &amp; Explanations &mdash; Form {form_letter}</h2>',
            '<div class="disclaimer">',
            '<strong>SCORING INSTRUCTIONS:</strong> Compare your responses from Section 2 against the key below. Mark each item correct or incorrect, then tally your domain scores in the diagnostic worksheet.',
            '</div>',
            '<h3>Domain Score Diagnostic Worksheet</h3>',
            '<table>',
            '<thead><tr><th>Domain</th><th>Code</th><th>Items</th><th>Your Score</th><th>Passing Target (&ge;70%)</th><th>Status</th></tr></thead>',
            '<tbody>',
            '<tr><td>Professional Relationships</td><td><code>prof-relationships</code></td><td>14</td><td>/ 14</td><td>10 / 14 (71%)</td><td>[ ] Target Met &nbsp; [ ] Review Needed</td></tr>',
            '<tr><td>Licensure and Regulations</td><td><code>licensure</code></td><td>13</td><td>/ 13</td><td>9 / 13 (69%)</td><td>[ ] Target Met &nbsp; [ ] Review Needed</td></tr>',
            '<tr><td>Competence</td><td><code>competence</code></td><td>9</td><td>/ 9</td><td>6 / 9 (67%)</td><td>[ ] Target Met &nbsp; [ ] Review Needed</td></tr>',
            '<tr><td>Assessment</td><td><code>assessment</code></td><td>6</td><td>/ 6</td><td>4 / 6 (67%)</td><td>[ ] Target Met &nbsp; [ ] Review Needed</td></tr>',
            '<tr><td>Privacy and Confidentiality</td><td><code>privacy</code></td><td>5</td><td>/ 5</td><td>4 / 5 (80%)</td><td>[ ] Target Met &nbsp; [ ] Review Needed</td></tr>',
            '<tr><td>Recordkeeping and Fees</td><td><code>recordkeeping</code></td><td>3</td><td>/ 3</td><td>2 / 3 (67%)</td><td>[ ] Target Met &nbsp; [ ] Review Needed</td></tr>',
            '<tr style="background-color: #ebf8ff; font-weight: bold;"><td>Total Examination</td><td>All Domains</td><td>50</td><td>/ 50</td><td>38 / 50 (76%)</td><td>[ ] PASS &nbsp; [ ] FAIL</td></tr>',
            '</tbody>',
            '</table>',
            '<h3>Quick-Reference Answer Key</h3>',
            '<table>',
            '<thead><tr><th style="width: 8%; text-align: center;">Q#</th><th style="width: 32%;">Domain</th><th style="width: 15%; text-align: center;">Correct Option</th><th style="width: 45%;">Legal Authority</th></tr></thead>',
            '<tbody>',
        ])

        for idx, q in enumerate(form_questions, 1):
            domain_name = DOMAIN_DISPLAY_NAMES.get(q.get("domain", ""), q.get("domain", ""))
            citation = q.get("source_citation", "").strip()
            correct_opt = q.get("correct_option", "").strip()
            html_parts.append(
                f'<tr>'
                f'<td style="text-align: center; font-weight: bold;">{idx}</td>'
                f'<td>{html.escape(domain_name)}</td>'
                f'<td style="text-align: center; font-weight: bold; color: #2b6cb0;">{html.escape(correct_opt)}</td>'
                f'<td><em>{html.escape(citation)}</em></td>'
                f'</tr>'
            )

        html_parts.extend([
            '</tbody>',
            '</table>',
            '<div class="page-break"></div>',
            '<h3>Detailed Item-by-Item Review</h3>',
        ])

        for idx, q in enumerate(form_questions, 1):
            domain_name = DOMAIN_DISPLAY_NAMES.get(q.get("domain", ""), q.get("domain", ""))
            correct_opt = q.get("correct_option", "").strip()
            citation = q.get("source_citation", "").strip()
            explanation = q.get("explanation", "").strip()

            html_parts.append('<div class="key-block">')
            html_parts.append(
                f'<div style="font-weight: bold; font-size: 10pt; color: #2c5282; margin-bottom: 2pt;">'
                f'Q{idx} (Pool Item #{html.escape(str(q.get("id", "")))}) &mdash; <span class="badge">{html.escape(domain_name)}</span> &mdash; '
                f'Correct Option: <strong style="color: #2b6cb0;">{html.escape(correct_opt)}</strong>'
                f'</div>'
            )
            if citation:
                html_parts.append(
                    f'<div style="font-size: 8.5pt; color: #4a5568; margin-bottom: 2pt;">'
                    f'<strong>Citation:</strong> <em>{html.escape(citation)}</em>'
                    f'</div>'
                )
            if explanation:
                html_parts.append(
                    f'<div style="font-size: 9pt; color: #2d3748;">'
                    f'<strong>Explanation:</strong> {html.escape(explanation)}'
                    f'</div>'
                )
            html_parts.append('</div>')

        html_parts.extend(["</body>", "</html>"])
        html_file.write_text("\n".join(html_parts), encoding="utf-8")

        # 3. Compile PDF
        compile_html_to_pdf(html_file, pdf_file)
        if output_dir is None and html_file.exists():
            html_file.unlink()

        forms_result[form_letter] = {
            "questions": form_questions,
            "md_path": md_file,
            "pdf_path": pdf_file,
        }

    return forms_result


WEB_QUIZZER_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Georgia Psychology Jurisprudence Examination — PSI Simulator &amp; Study Drill</title>
  <style>
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    :root {
      --bg-color: #f8fafc;
      --card-bg: #ffffff;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #64748b;
      --border-color: #cbd5e1;
      --primary: #1d4ed8;
      --primary-hover: #1e40af;
      --primary-light: #eff6ff;
      --success: #15803d;
      --success-bg: #f0fdf4;
      --success-border: #86efac;
      --danger: #b91c1c;
      --danger-bg: #fef2f2;
      --danger-border: #fca5a5;
      --warning: #b45309;
      --warning-bg: #fffbeb;
      --warning-border: #fcd34d;
      --flag-color: #d97706;
      --badge-bg: #e2e8f0;
      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.08);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Helvetica Neue", Arial, sans-serif;
      --radius: 8px;
    }

    [data-theme="dark"] {
      --bg-color: #0b1120;
      --card-bg: #1e293b;
      --text-primary: #f8fafc;
      --text-secondary: #cbd5e1;
      --text-muted: #94a3b8;
      --border-color: #334155;
      --primary: #3b82f6;
      --primary-hover: #60a5fa;
      --primary-light: #172554;
      --success: #22c55e;
      --success-bg: #052e16;
      --success-border: #166534;
      --danger: #ef4444;
      --danger-bg: #450a0a;
      --danger-border: #991b1b;
      --warning: #f59e0b;
      --warning-bg: #451a03;
      --warning-border: #92400e;
      --flag-color: #fbbf24;
      --badge-bg: #334155;
      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }

    body {
      font-family: var(--font-sans);
      background-color: var(--bg-color);
      color: var(--text-primary);
      line-height: 1.5;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    header {
      background-color: var(--card-bg);
      border-bottom: 1px solid var(--border-color);
      padding: 0.75rem 1.25rem;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: var(--shadow-sm);
    }

    .header-inner {
      max-width: 1050px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
    }

    .brand h1 {
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--primary);
      margin-bottom: 0.1rem;
    }

    .brand p {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .nav-tabs {
      display: flex;
      gap: 0.4rem;
      flex-wrap: wrap;
    }

    .nav-tab {
      background: transparent;
      border: 1px solid transparent;
      padding: 0.45rem 0.85rem;
      border-radius: var(--radius);
      font-size: 0.875rem;
      font-weight: 600;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }

    .nav-tab:hover {
      background-color: var(--primary-light);
      color: var(--primary);
    }

    .nav-tab.active {
      background-color: var(--primary);
      color: #ffffff;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .btn-icon {
      background: transparent;
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      border-radius: var(--radius);
      padding: 0.45rem 0.65rem;
      cursor: pointer;
      font-size: 0.875rem;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.35rem;
      transition: all 0.15s ease;
    }

    .btn-icon:hover {
      border-color: var(--primary);
      color: var(--primary);
    }

    main {
      flex: 1;
      max-width: 950px;
      width: 100%;
      margin: 0 auto;
      padding: 1.5rem 1rem;
    }

    .card {
      background-color: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: var(--radius);
      padding: 1.5rem;
      box-shadow: var(--shadow-sm);
      margin-bottom: 1.25rem;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.2rem 0.55rem;
      border-radius: 4px;
      background-color: var(--badge-bg);
      color: var(--text-secondary);
      letter-spacing: 0.02em;
    }

    .badge-primary {
      background-color: var(--primary-light);
      color: var(--primary);
      border: 1px solid var(--primary);
    }

    .badge-warning {
      background-color: var(--warning-bg);
      color: var(--warning);
      border: 1px solid var(--warning-border);
    }

    .badge-success {
      background-color: var(--success-bg);
      color: var(--success);
      border: 1px solid var(--success-border);
    }

    .badge-danger {
      background-color: var(--danger-bg);
      color: var(--danger);
      border: 1px solid var(--danger-border);
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.45rem;
      padding: 0.55rem 1.15rem;
      border-radius: var(--radius);
      font-weight: 600;
      font-size: 0.925rem;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.15s ease;
      text-decoration: none;
    }

    .btn:disabled {
      opacity: 0.45;
      cursor: not-allowed;
    }

    .btn-primary {
      background-color: var(--primary);
      color: #ffffff;
    }

    .btn-primary:hover:not(:disabled) {
      background-color: var(--primary-hover);
    }

    .btn-secondary {
      background-color: var(--card-bg);
      border-color: var(--border-color);
      color: var(--text-primary);
    }

    .btn-secondary:hover:not(:disabled) {
      background-color: var(--badge-bg);
    }

    .btn-outline {
      background: transparent;
      border-color: var(--border-color);
      color: var(--text-secondary);
    }

    .btn-outline:hover:not(:disabled) {
      border-color: var(--primary);
      color: var(--primary);
    }

    .btn-danger {
      background-color: var(--danger);
      color: #ffffff;
    }

    .btn-danger:hover:not(:disabled) {
      opacity: 0.9;
    }

    .btn-sm {
      padding: 0.35rem 0.65rem;
      font-size: 0.825rem;
    }

    .question-prompt {
      font-size: 1.125rem;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0.85rem 0 1.25rem 0;
      line-height: 1.5;
    }

    .options-list {
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
      margin-bottom: 1.25rem;
    }

    .option-btn {
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      width: 100%;
      text-align: left;
      background-color: var(--card-bg);
      border: 1.5px solid var(--border-color);
      border-radius: var(--radius);
      padding: 0.85rem 1rem;
      cursor: pointer;
      font-size: 0.95rem;
      color: var(--text-primary);
      line-height: 1.45;
      transition: all 0.15s ease;
    }

    .option-btn:hover:not(:disabled) {
      border-color: var(--primary);
      background-color: var(--primary-light);
    }

    .option-letter {
      flex-shrink: 0;
      width: 26px;
      height: 26px;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 0.825rem;
      background-color: var(--badge-bg);
      color: var(--text-secondary);
      margin-top: 2px;
      transition: all 0.15s ease;
    }

    .option-text {
      flex: 1;
    }

    .option-btn.selected {
      border-color: var(--primary);
      background-color: var(--primary-light);
      font-weight: 600;
    }

    .option-btn.selected .option-letter {
      background-color: var(--primary);
      color: #ffffff;
    }

    .option-btn.correct {
      border-color: var(--success-border) !important;
      background-color: var(--success-bg) !important;
      color: var(--success) !important;
      font-weight: 600;
    }

    .option-btn.correct .option-letter {
      background-color: var(--success) !important;
      color: #ffffff !important;
    }

    .option-btn.incorrect {
      border-color: var(--danger-border) !important;
      background-color: var(--danger-bg) !important;
      color: var(--danger) !important;
    }

    .option-btn.incorrect .option-letter {
      background-color: var(--danger) !important;
      color: #ffffff !important;
    }

    .feedback-box {
      margin-top: 1rem;
      padding: 1rem 1.25rem;
      border-radius: var(--radius);
      border-left: 4px solid var(--primary);
      background-color: var(--primary-light);
    }

    .feedback-box.is-correct {
      border-left-color: var(--success);
      background-color: var(--success-bg);
    }

    .feedback-box.is-incorrect {
      border-left-color: var(--danger);
      background-color: var(--danger-bg);
    }

    .feedback-status {
      font-weight: 700;
      font-size: 0.975rem;
      margin-bottom: 0.35rem;
    }

    .feedback-status.correct {
      color: var(--success);
    }

    .feedback-status.incorrect {
      color: var(--danger);
    }

    .citation-line {
      font-size: 0.875rem;
      font-weight: 600;
      color: var(--primary);
      margin-bottom: 0.4rem;
    }

    .explanation-text {
      font-size: 0.9rem;
      color: var(--text-primary);
      line-height: 1.5;
    }

    .exam-status-bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      padding-bottom: 0.85rem;
      margin-bottom: 0.85rem;
      border-bottom: 1px solid var(--border-color);
    }

    .timer-display {
      font-size: 1.15rem;
      font-weight: 700;
      font-family: monospace;
      color: var(--text-primary);
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
    }

    .jump-grid {
      display: grid;
      grid-template-columns: repeat(10, 1fr);
      gap: 0.4rem;
      margin: 1.25rem 0;
    }

    @media (max-width: 640px) {
      main {
        padding: 1rem 0.5rem;
      }
      .card {
        padding: 1rem;
      }
      .jump-grid {
        grid-template-columns: repeat(5, 1fr);
      }
    }

    .grid-cell {
      aspect-ratio: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--border-color);
      background-color: var(--card-bg);
      color: var(--text-secondary);
      font-weight: 600;
      font-size: 0.85rem;
      border-radius: 4px;
      cursor: pointer;
      position: relative;
      transition: all 0.15s ease;
      font-family: inherit;
    }

    .grid-cell:hover {
      border-color: var(--primary);
      color: var(--primary);
    }

    .grid-cell.answered {
      background-color: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }

    .grid-cell.current {
      box-shadow: 0 0 0 2px var(--card-bg), 0 0 0 4px var(--primary);
      font-weight: 700;
    }

    .grid-cell.flagged::after {
      content: "⚑";
      position: absolute;
      top: 1px;
      right: 2px;
      font-size: 0.7rem;
      color: var(--flag-color);
    }

    .grid-cell.answered.flagged::after {
      color: #fbbf24;
    }

    .grid-legend {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      font-size: 0.825rem;
      color: var(--text-muted);
      margin-bottom: 0.5rem;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }

    .legend-box {
      width: 14px;
      height: 14px;
      border-radius: 3px;
      border: 1px solid var(--border-color);
    }

    .legend-box.unanswered {
      background-color: var(--card-bg);
    }

    .legend-box.answered {
      background-color: var(--primary);
      border-color: var(--primary);
    }

    .legend-box.flagged {
      background-color: var(--card-bg);
      border-color: var(--flag-color);
      position: relative;
    }

    .legend-box.flagged::after {
      content: "⚑";
      font-size: 0.65rem;
      color: var(--flag-color);
      position: absolute;
      top: -1px;
      left: 2px;
    }

    .legend-box.current {
      box-shadow: 0 0 0 2px var(--primary);
    }

    .report-table {
      width: 100%;
      border-collapse: collapse;
      margin: 1.25rem 0;
      font-size: 0.9rem;
    }

    .report-table th, .report-table td {
      padding: 0.65rem 0.75rem;
      border: 1px solid var(--border-color);
      text-align: left;
    }

    .report-table th {
      background-color: var(--badge-bg);
      font-weight: 700;
      color: var(--text-primary);
    }

    .report-table tr:nth-child(even) td {
      background-color: var(--primary-light);
    }

    .report-total-row {
      font-weight: 700;
      background-color: var(--primary-light) !important;
    }

    .modal-overlay {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(0, 0, 0, 0.55);
      backdrop-filter: blur(2px);
      z-index: 200;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    }

    .modal-overlay.open {
      display: flex;
    }

    .modal-box {
      background-color: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: var(--radius);
      max-width: 640px;
      width: 100%;
      max-height: 90vh;
      overflow-y: auto;
      padding: 1.5rem;
      box-shadow: var(--shadow-lg);
    }

    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 0.75rem;
      margin-bottom: 1rem;
    }

    .modal-title {
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-primary);
    }

    .modal-close {
      background: transparent;
      border: none;
      font-size: 1.35rem;
      cursor: pointer;
      color: var(--text-muted);
      line-height: 1;
    }

    .modal-footer {
      display: flex;
      justify-content: flex-end;
      gap: 0.75rem;
      border-top: 1px solid var(--border-color);
      padding-top: 1rem;
      margin-top: 1rem;
    }

    .shortcuts-list {
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }

    .shortcut-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.45rem 0;
      border-bottom: 1px solid var(--border-color);
      font-size: 0.9rem;
    }

    kbd {
      display: inline-block;
      padding: 0.2rem 0.5rem;
      font-size: 0.8rem;
      font-family: monospace;
      font-weight: 600;
      color: var(--text-primary);
      background-color: var(--badge-bg);
      border: 1px solid var(--border-color);
      border-radius: 4px;
      box-shadow: 0 1px 1px rgba(0, 0, 0, 0.15);
    }

    .domain-filters-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      margin-bottom: 1.25rem;
    }

    .filter-btn {
      background-color: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: var(--radius);
      padding: 0.4rem 0.75rem;
      font-size: 0.825rem;
      font-weight: 600;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .filter-btn:hover {
      border-color: var(--primary);
      color: var(--primary);
    }

    .filter-btn.active {
      background-color: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }

    footer {
      background-color: var(--card-bg);
      border-top: 1px solid var(--border-color);
      padding: 1.25rem;
      margin-top: auto;
      font-size: 0.8rem;
      color: var(--text-muted);
      line-height: 1.5;
    }

    .footer-inner {
      max-width: 1050px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .actions-footer {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      margin-top: 1.25rem;
      padding-top: 1rem;
      border-top: 1px solid var(--border-color);
    }

    .actions-group {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .empty-state {
      text-align: center;
      padding: 3rem 1rem;
      color: var(--text-muted);
    }

    .empty-state h3 {
      font-size: 1.35rem;
      color: var(--text-primary);
      margin-bottom: 0.5rem;
    }

    .empty-state p {
      max-width: 500px;
      margin: 0 auto 1.5rem auto;
      font-size: 0.95rem;
    }
  </style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="brand">
      <h1>Georgia Psychology Jurisprudence Examination</h1>
      <p>Candidate Study Quizzer &amp; PSI Simulation System &bull; <span class="badge" style="background: rgba(43, 108, 176, 0.15); color: var(--primary); font-size: 0.75rem; padding: 1px 6px; border-radius: 9999px;">Question Pool v1.0 (10/25/2026)</span></p>
    </div>
    <nav class="nav-tabs">
      <button class="nav-tab active" id="tab-psi" onclick="switchMode('psi')">
        <span>⏱️</span> PSI Exam Simulation
      </button>
      <button class="nav-tab" id="tab-drill" onclick="switchMode('drill')">
        <span>📚</span> Domain Study Drill
      </button>
      <button class="nav-tab" id="tab-missed" onclick="switchMode('missed')">
        <span>⚠️</span> Missed Questions <span class="badge" id="missed-badge">0</span>
      </button>
    </nav>
    <div class="header-actions">
      <button class="btn-icon" id="theme-toggle-btn" onclick="toggleTheme()" title="Toggle Dark/Light Mode">🌙 Dark</button>
      <button class="btn-icon" onclick="openShortcutsModal()" title="Keyboard Shortcuts">⌨️ Shortcuts</button>
    </div>
  </div>
</header>

<main id="app-container">
  <!-- Dynamic Views Injected by JS -->
</main>

<footer>
  <div class="footer-inner">
    <p><strong>LEGAL DISCLAIMER:</strong> __LEGAL_DISCLAIMER__</p>
    <p>Georgia Psychology Jurisprudence Examination Self-Study Resource &bull; <strong>Question Pool:</strong> Version 1.0 (10/25/2026) &bull; 100% Offline Standalone Application &bull; Runs completely locally without network dependencies.</p>
  </div>
</footer>

<!-- Modals -->
<div class="modal-overlay" id="jump-grid-modal" onclick="handleModalBackdropClick(event, 'jump-grid-modal')">
  <div class="modal-box">
    <div class="modal-header">
      <h3 class="modal-title">PSI Exam Jump Grid</h3>
      <button class="modal-close" onclick="closeJumpGrid()">&times;</button>
    </div>
    <div class="grid-legend">
      <div class="legend-item"><span class="legend-box unanswered"></span> Unanswered</div>
      <div class="legend-item"><span class="legend-box answered"></span> Answered</div>
      <div class="legend-item"><span class="legend-box flagged"></span> Flagged</div>
      <div class="legend-item"><span class="legend-box current"></span> Current</div>
    </div>
    <div class="jump-grid" id="jump-grid-container"></div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeJumpGrid()">Close Grid</button>
      <button class="btn btn-primary" onclick="confirmSubmitPsiExam()">Submit Exam</button>
    </div>
  </div>
</div>

<div class="modal-overlay" id="shortcuts-modal" onclick="handleModalBackdropClick(event, 'shortcuts-modal')">
  <div class="modal-box">
    <div class="modal-header">
      <h3 class="modal-title">Keyboard Shortcuts</h3>
      <button class="modal-close" onclick="closeShortcutsModal()">&times;</button>
    </div>
    <div class="shortcuts-list">
      <div class="shortcut-item"><span>Select option A, B, C, or D</span><div><kbd>A</kbd> <kbd>B</kbd> <kbd>C</kbd> <kbd>D</kbd> or <kbd>1</kbd> <kbd>2</kbd> <kbd>3</kbd> <kbd>4</kbd></div></div>
      <div class="shortcut-item"><span>Advance to next question</span><div><kbd>N</kbd> or <kbd>&rarr;</kbd></div></div>
      <div class="shortcut-item"><span>Go to previous question</span><div><kbd>P</kbd> or <kbd>&larr;</kbd></div></div>
      <div class="shortcut-item"><span>Toggle question flag (PSI simulation)</span><div><kbd>F</kbd></div></div>
      <div class="shortcut-item"><span>Confirm / Advance in study drill</span><div><kbd>Enter</kbd></div></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeShortcutsModal()">Close</button>
    </div>
  </div>
</div>

<script>
// QUESTION BANK AND METADATA
const QUESTION_BANK = __QUESTION_BANK_JSON__;
const DOMAIN_NAMES = __DOMAIN_DISPLAY_NAMES_JSON__;
const DOMAIN_QUOTAS = __DOMAIN_QUOTAS_JSON__;
const PASS_SCORE = 38; // 38 / 50 (76%)

// STATE MANAGEMENT
const state = {
  mode: 'psi', // 'psi' | 'drill' | 'missed'
  psi: {
    status: 'intro', // 'intro' | 'active' | 'results' | 'review'
    questions: [],
    currentIndex: 0,
    answers: {},
    flagged: {},
    timerSeconds: 3600,
    timerInterval: null,
    lastResults: null,
    reviewFilter: 'all', // 'all' | 'missed'
    reviewIndices: [],
    reviewCurrentPos: 0
  },
  drill: {
    domain: 'all',
    questions: [],
    currentIndex: 0,
    answered: {},
    shuffled: false
  },
  missed: {
    questions: [],
    currentIndex: 0,
    answered: {}
  }
};

// STORAGE UTILITIES WITH SAFE FALLBACK (Private Browsing / file:// origins / quota errors)
const storage = {
  _mem: {},
  get(key) {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        return window.localStorage.getItem(key);
      }
    } catch (e) {
      // In private browsing or file:// context, use in-memory fallback
    }
    return Object.prototype.hasOwnProperty.call(this._mem, key) ? this._mem[key] : null;
  },
  set(key, val) {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem(key, val);
      }
    } catch (e) {
      // In private browsing or quota exceeded, use in-memory fallback
    }
    this._mem[key] = String(val);
  }
};

function getMissedQuestions() {
  try {
    const raw = storage.get('gamb_missed_questions');
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    return [];
  }
}

function saveMissedQuestions(ids) {
  try {
    const unique = [...new Set(ids)];
    storage.set('gamb_missed_questions', JSON.stringify(unique));
    updateMissedBadge();
  } catch (e) {
    console.error("Failed to save missed questions", e);
  }
}

function addMissedQuestion(id) {
  const current = getMissedQuestions();
  if (!current.includes(id)) {
    current.push(id);
    saveMissedQuestions(current);
  }
}

function removeMissedQuestion(id) {
  const current = getMissedQuestions().filter(item => item !== id);
  saveMissedQuestions(current);
}

function clearAllMissedQuestions() {
  saveMissedQuestions([]);
}

function updateMissedBadge() {
  const badge = document.getElementById('missed-badge');
  if (badge) {
    const count = getMissedQuestions().length;
    badge.textContent = count;
    badge.style.display = count > 0 ? 'inline-flex' : 'none';
  }
}

// THEME HANDLING
function initTheme() {
  try {
    const saved = storage.get('gamb_theme');
    if (saved) {
      document.documentElement.setAttribute('data-theme', saved);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  } catch (e) {
    // Graceful fallback
  }
  updateThemeButton();
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const newTheme = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', newTheme);
  storage.set('gamb_theme', newTheme);
  updateThemeButton();
}

function updateThemeButton() {
  const btn = document.getElementById('theme-toggle-btn');
  if (!btn) return;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  btn.innerHTML = isDark ? '<span>☀️</span> Light' : '<span>🌙</span> Dark';
}

// UTILITIES
function escapeHtml(str) {
  if (str === undefined || str === null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatTime(totalSecs) {
  const m = Math.floor(totalSecs / 60);
  const s = totalSecs % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

// MODE SWITCHING
function switchMode(newMode) {
  state.mode = newMode;
  document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
  const activeTab = document.getElementById('tab-' + newMode);
  if (activeTab) activeTab.classList.add('active');

  if (newMode === 'drill' && state.drill.questions.length === 0) {
    initDrillQuestions();
  } else if (newMode === 'missed') {
    initMissedQuestions();
  }

  render();
}

// ==========================================
// PSI EXAM SIMULATION
// ==========================================
function startPsiExam() {
  const byDomain = {};
  for (const d of Object.keys(DOMAIN_QUOTAS)) byDomain[d] = [];
  for (const q of QUESTION_BANK) {
    if (byDomain[q.domain]) byDomain[q.domain].push(q);
  }

  const selected = [];
  for (const [dom, quota] of Object.entries(DOMAIN_QUOTAS)) {
    const pool = [...byDomain[dom]];
    for (let i = pool.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [pool[i], pool[j]] = [pool[j], pool[i]];
    }
    selected.push(...pool.slice(0, quota));
  }

  for (let i = selected.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [selected[i], selected[j]] = [selected[j], selected[i]];
  }

  // Shuffle options to prevent position bias
  state.psi.questions = selected.map(q => {
    const origKeys = ["A", "B", "C", "D"];
    const shuffledKeys = [...origKeys];
    for (let i = shuffledKeys.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffledKeys[i], shuffledKeys[j]] = [shuffledKeys[j], shuffledKeys[i]];
    }
    const newOptions = {};
    let newCorrect = "A";
    origKeys.forEach((key, idx) => {
      const srcKey = shuffledKeys[idx];
      newOptions[key] = q.options[srcKey];
      if (srcKey === q.correct_option) {
        newCorrect = key;
      }
    });
    return {
      ...q,
      options: newOptions,
      correct_option: newCorrect
    };
  });

  state.psi.currentIndex = 0;
  state.psi.answers = {};
  state.psi.flagged = {};
  state.psi.timerSeconds = 3600; // 60 minutes
  state.psi.status = 'active';

  if (state.psi.timerInterval) clearInterval(state.psi.timerInterval);
  state.psi.timerInterval = setInterval(() => {
    state.psi.timerSeconds--;
    updatePsiTimer();
    if (state.psi.timerSeconds <= 0) {
      clearInterval(state.psi.timerInterval);
      state.psi.timerInterval = null;
      alert("Time has expired (60 minutes). Your examination will now be submitted.");
      switchMode('psi');
      submitPsiExam();
    }
  }, 1000);

  render();
}

function updatePsiTimer() {
  const timerEl = document.getElementById('psi-timer');
  if (!timerEl) return;
  timerEl.textContent = '⏱️ ' + formatTime(state.psi.timerSeconds);
  if (state.psi.timerSeconds < 300) {
    timerEl.style.color = 'var(--danger)';
    timerEl.style.fontWeight = 'bold';
  } else if (state.psi.timerSeconds < 600) {
    timerEl.style.color = 'var(--warning)';
  } else {
    timerEl.style.color = 'inherit';
  }
}

function selectPsiOption(letter) {
  if (state.psi.status !== 'active') return;
  state.psi.answers[state.psi.currentIndex] = letter;
  render();
}

function togglePsiFlag() {
  if (state.psi.status !== 'active') return;
  const idx = state.psi.currentIndex;
  state.psi.flagged[idx] = !state.psi.flagged[idx];
  render();
}

function psiNext() {
  if (state.psi.currentIndex < state.psi.questions.length - 1) {
    state.psi.currentIndex++;
    render();
  }
}

function psiPrev() {
  if (state.psi.currentIndex > 0) {
    state.psi.currentIndex--;
    render();
  }
}

function confirmSubmitPsiExam() {
  closeJumpGrid();
  const answeredCount = Object.keys(state.psi.answers).length;
  const unanswered = 50 - answeredCount;
  if (unanswered > 0) {
    if (!confirm(`You have ${unanswered} unanswered question(s). Are you sure you want to finish and submit your examination?`)) {
      return;
    }
  } else {
    if (!confirm("Are you ready to submit your examination and view your diagnostic score report?")) {
      return;
    }
  }
  submitPsiExam();
}

function submitPsiExam() {
  if (state.psi.timerInterval) {
    clearInterval(state.psi.timerInterval);
    state.psi.timerInterval = null;
  }

  let score = 0;
  const missedIds = [];
  const domainScores = {};
  for (const d of Object.keys(DOMAIN_QUOTAS)) {
    domainScores[d] = { correct: 0, total: DOMAIN_QUOTAS[d] };
  }

  state.psi.questions.forEach((q, idx) => {
    const userAns = state.psi.answers[idx];
    if (userAns === q.correct_option) {
      score++;
      if (domainScores[q.domain]) domainScores[q.domain].correct++;
    } else {
      missedIds.push(q.id);
    }
  });

  // Record missed questions
  missedIds.forEach(id => addMissedQuestion(id));

  state.psi.lastResults = {
    score: score,
    total: 50,
    percentage: Math.round((score / 50) * 100),
    passed: score >= PASS_SCORE,
    domainScores: domainScores,
    missedIds: missedIds
  };

  state.psi.status = 'results';
  render();
}

function startPsiReview(filter) {
  state.psi.reviewFilter = filter;
  if (filter === 'missed') {
    state.psi.reviewIndices = state.psi.questions
      .map((q, idx) => (state.psi.answers[idx] !== q.correct_option ? idx : null))
      .filter(idx => idx !== null);
  } else {
    state.psi.reviewIndices = state.psi.questions.map((_, idx) => idx);
  }
  if (state.psi.reviewIndices.length === 0) {
    state.psi.reviewIndices = state.psi.questions.map((_, idx) => idx);
    state.psi.reviewFilter = 'all';
  }
  state.psi.reviewCurrentPos = 0;
  state.psi.status = 'review';
  render();
}

function psiReviewNext() {
  if (state.psi.reviewCurrentPos < state.psi.reviewIndices.length - 1) {
    state.psi.reviewCurrentPos++;
    render();
  }
}

function psiReviewPrev() {
  if (state.psi.reviewCurrentPos > 0) {
    state.psi.reviewCurrentPos--;
    render();
  }
}

function openJumpGrid() {
  const container = document.getElementById('jump-grid-container');
  if (!container) return;

  container.innerHTML = '';
  for (let i = 0; i < 50; i++) {
    const cell = document.createElement('button');
    cell.type = 'button';
    cell.className = 'grid-cell';
    cell.textContent = i + 1;
    cell.setAttribute('aria-label', `Question ${i + 1}`);

    if (state.psi.answers[i] !== undefined) cell.classList.add('answered');
    if (state.psi.flagged[i]) cell.classList.add('flagged');
    if (i === state.psi.currentIndex) cell.classList.add('current');

    cell.onclick = () => {
      state.psi.currentIndex = i;
      closeJumpGrid();
      render();
    };
    container.appendChild(cell);
  }

  document.getElementById('jump-grid-modal').classList.add('open');
}

function closeJumpGrid() {
  document.getElementById('jump-grid-modal').classList.remove('open');
}

// ==========================================
// DOMAIN STUDY DRILL
// ==========================================
function initDrillQuestions() {
  let list = [];
  if (state.drill.domain === 'all') {
    list = [...QUESTION_BANK];
  } else {
    list = QUESTION_BANK.filter(q => q.domain === state.drill.domain);
  }

  if (state.drill.shuffled) {
    for (let i = list.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [list[i], list[j]] = [list[j], list[i]];
    }
  }
  state.drill.questions = list;
  state.drill.currentIndex = 0;
}

function setDrillDomain(dom) {
  state.drill.domain = dom;
  initDrillQuestions();
  render();
}

function toggleDrillShuffle() {
  state.drill.shuffled = !state.drill.shuffled;
  initDrillQuestions();
  render();
}

function selectDrillOption(letter) {
  const currentQ = state.drill.questions[state.drill.currentIndex];
  if (!currentQ || state.drill.answered[currentQ.id]) return;

  state.drill.answered[currentQ.id] = letter;
  if (letter !== currentQ.correct_option) {
    addMissedQuestion(currentQ.id);
  }
  render();
}

function drillNext() {
  if (state.drill.currentIndex < state.drill.questions.length - 1) {
    state.drill.currentIndex++;
    render();
  }
}

function drillPrev() {
  if (state.drill.currentIndex > 0) {
    state.drill.currentIndex--;
    render();
  }
}

function drillJump(index) {
  if (!isNaN(index) && index >= 0 && index < state.drill.questions.length) {
    state.drill.currentIndex = index;
    render();
  } else {
    render();
  }
}

// ==========================================
// MISSED QUESTIONS DRILL
// ==========================================
function initMissedQuestions() {
  const missedIds = getMissedQuestions();
  state.missed.questions = QUESTION_BANK.filter(q => missedIds.includes(q.id));
  if (state.missed.currentIndex >= state.missed.questions.length) {
    state.missed.currentIndex = Math.max(0, state.missed.questions.length - 1);
  }
}

function selectMissedOption(letter) {
  const currentQ = state.missed.questions[state.missed.currentIndex];
  if (!currentQ || state.missed.answered[currentQ.id]) return;

  state.missed.answered[currentQ.id] = letter;
  render();
}

function missedNext() {
  if (state.missed.currentIndex < state.missed.questions.length - 1) {
    state.missed.currentIndex++;
    render();
  }
}

function missedPrev() {
  if (state.missed.currentIndex > 0) {
    state.missed.currentIndex--;
    render();
  }
}

function removeCurrentMissed(id) {
  removeMissedQuestion(id);
  initMissedQuestions();
  render();
}

function handleClearAllMissed() {
  if (confirm("Are you sure you want to clear all missed questions from your local review queue?")) {
    clearAllMissedQuestions();
    initMissedQuestions();
    render();
  }
}

// ==========================================
// MODALS & KEYBOARD
// ==========================================
function openShortcutsModal() {
  document.getElementById('shortcuts-modal').classList.add('open');
}

function closeShortcutsModal() {
  document.getElementById('shortcuts-modal').classList.remove('open');
}

function handleModalBackdropClick(event, modalId) {
  if (event.target && event.target.id === modalId) {
    document.getElementById(modalId).classList.remove('open');
  }
}

window.addEventListener('keydown', (e) => {
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;
  const key = e.key.toUpperCase();

  if (key === 'ESCAPE') {
    closeJumpGrid();
    closeShortcutsModal();
    return;
  }

  if (state.mode === 'psi') {
    if (state.psi.status === 'active') {
      if (['A', 'B', 'C', 'D'].includes(key)) selectPsiOption(key);
      else if (key === '1') selectPsiOption('A');
      else if (key === '2') selectPsiOption('B');
      else if (key === '3') selectPsiOption('C');
      else if (key === '4') selectPsiOption('D');
      else if (key === 'F') togglePsiFlag();
      else if (key === 'N' || e.key === 'ArrowRight') psiNext();
      else if (key === 'P' || e.key === 'ArrowLeft') psiPrev();
      else if (key === 'ENTER') psiNext();
    } else if (state.psi.status === 'review') {
      if (key === 'N' || key === 'ENTER' || e.key === 'ArrowRight') psiReviewNext();
      else if (key === 'P' || e.key === 'ArrowLeft') psiReviewPrev();
    }
  } else if (state.mode === 'drill') {
    if (['A', 'B', 'C', 'D'].includes(key)) selectDrillOption(key);
    else if (key === '1') selectDrillOption('A');
    else if (key === '2') selectDrillOption('B');
    else if (key === '3') selectDrillOption('C');
    else if (key === '4') selectDrillOption('D');
    else if (key === 'N' || key === 'ENTER' || e.key === 'ArrowRight') drillNext();
    else if (key === 'P' || e.key === 'ArrowLeft') drillPrev();
  } else if (state.mode === 'missed') {
    if (['A', 'B', 'C', 'D'].includes(key)) selectMissedOption(key);
    else if (key === '1') selectMissedOption('A');
    else if (key === '2') selectMissedOption('B');
    else if (key === '3') selectMissedOption('C');
    else if (key === '4') selectMissedOption('D');
    else if (key === 'N' || key === 'ENTER' || e.key === 'ArrowRight') missedNext();
    else if (key === 'P' || e.key === 'ArrowLeft') missedPrev();
  }
});

// ==========================================
// RENDERERS
// ==========================================
function render() {
  const container = document.getElementById('app-container');
  if (!container) return;

  if (state.mode === 'psi') {
    renderPsi(container);
  } else if (state.mode === 'drill') {
    renderDrill(container);
  } else if (state.mode === 'missed') {
    renderMissed(container);
  }

  updateMissedBadge();
}

function renderPsi(container) {
  if (state.psi.status === 'intro') {
    container.innerHTML = `
      <div class="card" style="max-width: 780px; margin: 1.5rem auto;">
        <h2 style="font-size: 1.5rem; color: var(--primary); margin-bottom: 0.75rem;">PSI Exam Simulation</h2>
        <p style="color: var(--text-secondary); margin-bottom: 1.25rem; font-size: 1rem;">
          This timed simulation replicates the exact examination environment administered by PSI Services for the Georgia Board of Examiners of Psychologists.
        </p>

        <div style="background-color: var(--primary-light); border-left: 4px solid var(--primary); padding: 1rem 1.25rem; border-radius: var(--radius); margin-bottom: 1.5rem;">
          <h4 style="font-weight: 700; color: var(--primary); margin-bottom: 0.5rem;">Official Examination Parameters</h4>
          <ul style="margin-left: 1.25rem; color: var(--text-secondary); font-size: 0.925rem; line-height: 1.6;">
            <li><strong>50 Multiple-Choice Questions:</strong> Sampled strictly according to official Georgia Board domain quotas.</li>
            <li><strong>60-Minute Countdown Timer:</strong> Real-time timer with alerts when under 10 and 5 minutes.</li>
            <li><strong>76% Passing Score Target:</strong> Must achieve at least 38 out of 50 correct answers to pass.</li>
            <li><strong>Navigation &amp; Review:</strong> Ability to flag items, jump across questions via a 5x10 grid, and review all answers post-submission.</li>
            <li><strong>Targeted Remediation:</strong> Missed questions are automatically saved to your browser review queue.</li>
          </ul>
        </div>

        <h4 style="font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">Domain Distribution Quotas</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.65rem; margin-bottom: 1.5rem;">
          <div style="background: var(--card-bg); border: 1px solid var(--border-color); padding: 0.65rem 0.85rem; border-radius: var(--radius); font-size: 0.875rem;">
            <strong>Professional Relationships:</strong> 14 items (28%)
          </div>
          <div style="background: var(--card-bg); border: 1px solid var(--border-color); padding: 0.65rem 0.85rem; border-radius: var(--radius); font-size: 0.875rem;">
            <strong>Licensure and Regulations:</strong> 13 items (26%)
          </div>
          <div style="background: var(--card-bg); border: 1px solid var(--border-color); padding: 0.65rem 0.85rem; border-radius: var(--radius); font-size: 0.875rem;">
            <strong>Competence:</strong> 9 items (18%)
          </div>
          <div style="background: var(--card-bg); border: 1px solid var(--border-color); padding: 0.65rem 0.85rem; border-radius: var(--radius); font-size: 0.875rem;">
            <strong>Assessment:</strong> 6 items (12%)
          </div>
          <div style="background: var(--card-bg); border: 1px solid var(--border-color); padding: 0.65rem 0.85rem; border-radius: var(--radius); font-size: 0.875rem;">
            <strong>Privacy &amp; Confidentiality:</strong> 5 items (10%)
          </div>
          <div style="background: var(--card-bg); border: 1px solid var(--border-color); padding: 0.65rem 0.85rem; border-radius: var(--radius); font-size: 0.875rem;">
            <strong>Recordkeeping &amp; Fees:</strong> 3 items (6%)
          </div>
        </div>

        <div style="text-align: center; padding-top: 0.5rem;">
          <button class="btn btn-primary" style="padding: 0.8rem 2.2rem; font-size: 1.05rem;" onclick="startPsiExam()">
            Begin Timed Simulation (50 Questions)
          </button>
        </div>
      </div>
    `;
    return;
  }

  if (state.psi.status === 'active') {
    const q = state.psi.questions[state.psi.currentIndex];
    const userAns = state.psi.answers[state.psi.currentIndex];
    const isFlagged = !!state.psi.flagged[state.psi.currentIndex];
    const answeredCount = Object.keys(state.psi.answers).length;
    const domainName = DOMAIN_NAMES[q.domain] || q.domain;

    container.innerHTML = `
      <div class="card">
        <div class="exam-status-bar">
          <div>
            <span style="font-weight: 700; font-size: 1.05rem; color: var(--primary);">Question ${state.psi.currentIndex + 1}</span>
            <span style="color: var(--text-muted); font-size: 0.95rem;"> of 50</span>
          </div>
          <div class="timer-display" id="psi-timer">
            ⏱️ ${formatTime(state.psi.timerSeconds)}
          </div>
          <div class="actions-group">
            <button class="btn btn-sm ${isFlagged ? 'btn-warning' : 'btn-outline'}" onclick="togglePsiFlag()" title="Toggle flag [F]">
              ${isFlagged ? '🚩 Flagged' : '⚑ Flag [F]'}
            </button>
            <button class="btn btn-sm btn-secondary" onclick="openJumpGrid()" title="Open 5x10 Question Jump Grid">
              ☰ Grid (${answeredCount}/50)
            </button>
          </div>
        </div>

        <div style="display: flex; gap: 0.4rem; margin-bottom: 0.75rem;">
          <span class="badge badge-primary">${escapeHtml(domainName)}</span>
          ${q.subtopic ? `<span class="badge">${escapeHtml(q.subtopic)}</span>` : ''}
        </div>

        <div class="question-prompt">${escapeHtml(q.question_text)}</div>

        <div class="options-list">
          ${["A", "B", "C", "D"].map(letter => `
            <button class="option-btn ${userAns === letter ? 'selected' : ''}" onclick="selectPsiOption('${letter}')">
              <span class="option-letter">${letter}</span>
              <span class="option-text">${escapeHtml(q.options[letter])}</span>
            </button>
          `).join('')}
        </div>

        <div class="actions-footer">
          <div class="actions-group">
            <button class="btn btn-secondary" onclick="psiPrev()" ${state.psi.currentIndex === 0 ? 'disabled' : ''}>
              &larr; Previous [P]
            </button>
            <button class="btn btn-secondary" onclick="psiNext()" ${state.psi.currentIndex === 49 ? 'disabled' : ''}>
              Next [N] &rarr;
            </button>
          </div>
          <div>
            <button class="btn btn-primary" onclick="confirmSubmitPsiExam()">
              Submit Exam
            </button>
          </div>
        </div>
      </div>
    `;
    updatePsiTimer();
    return;
  }

  if (state.psi.status === 'results') {
    const res = state.psi.lastResults;
    const passed = res.passed;

    container.innerHTML = `
      <div class="card" style="max-width: 820px; margin: 1.5rem auto;">
        <div style="text-align: center; padding: 1.5rem 1rem; border-radius: var(--radius); background-color: ${passed ? 'var(--success-bg)' : 'var(--danger-bg)'}; border: 1.5px solid ${passed ? 'var(--success-border)' : 'var(--danger-border)'}; margin-bottom: 1.5rem;">
          <div style="font-size: 2.2rem; font-weight: 800; color: ${passed ? 'var(--success)' : 'var(--danger)'}; margin-bottom: 0.35rem;">
            ${passed ? '✓ PASSED' : '✗ DID NOT PASS'}
          </div>
          <div style="font-size: 1.35rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.25rem;">
            Score: ${res.score} / 50 &bull; ${res.percentage}%
          </div>
          <div style="font-size: 0.95rem; color: var(--text-secondary);">
            Official Georgia Passing Threshold: <strong>38 / 50 (76%)</strong>
          </div>
        </div>

        <h3 style="font-size: 1.15rem; color: var(--text-primary); margin-bottom: 0.75rem;">Diagnostic Domain Breakdown</h3>
        <div style="overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 1.25rem 0;">
        <table class="report-table" style="margin: 0;">
          <thead>
            <tr>
              <th>Domain</th>
              <th style="width: 15%; text-align: center;">Score</th>
              <th style="width: 25%; text-align: center;">Target (&ge;70%)</th>
              <th style="width: 20%; text-align: center;">Status</th>
            </tr>
          </thead>
          <tbody>
            ${Object.entries(res.domainScores).map(([dom, data]) => {
              const domName = DOMAIN_NAMES[dom] || dom;
              const targetMet = (data.correct / data.total) >= 0.7;
              return `
                <tr>
                  <td><strong>${escapeHtml(domName)}</strong></td>
                  <td style="text-align: center;">${data.correct} / ${data.total}</td>
                  <td style="text-align: center;">&ge;70%</td>
                  <td style="text-align: center;">
                    <span class="badge ${targetMet ? 'badge-success' : 'badge-warning'}">
                      ${targetMet ? 'Target Met' : 'Review Needed'}
                    </span>
                  </td>
                </tr>
              `;
            }).join('')}
            <tr class="report-total-row">
              <td><strong>Total Examination</strong></td>
              <td style="text-align: center;"><strong>${res.score} / 50</strong></td>
              <td style="text-align: center;"><strong>&ge;76% (38/50)</strong></td>
              <td style="text-align: center;">
                <span class="badge ${passed ? 'badge-success' : 'badge-danger'}">
                  ${passed ? 'PASS' : 'FAIL'}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        </div>

        ${res.missedIds.length > 0 ? `
          <div style="background-color: var(--warning-bg); border: 1px solid var(--warning-border); border-radius: var(--radius); padding: 0.85rem 1rem; margin-bottom: 1.5rem; font-size: 0.9rem; color: var(--warning);">
            <strong>Remediation Note:</strong> All ${res.missedIds.length} missed question(s) have been saved to your <strong>Missed Questions</strong> queue for targeted practice.
          </div>
        ` : ''}

        <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 0.75rem; padding-top: 0.5rem;">
          <button class="btn btn-primary" onclick="startPsiReview('all')">
            Review All 50 Questions
          </button>
          ${res.missedIds.length > 0 ? `
            <button class="btn btn-secondary" onclick="startPsiReview('missed')">
              Review Missed Only (${res.missedIds.length})
            </button>
          ` : ''}
          <button class="btn btn-outline" onclick="startPsiExam()">
            Retake New Exam Simulation
          </button>
        </div>
      </div>
    `;
    return;
  }

  if (state.psi.status === 'review') {
    const qIdx = state.psi.reviewIndices[state.psi.reviewCurrentPos];
    const q = state.psi.questions[qIdx];
    const userAns = state.psi.answers[qIdx];
    const isCorrect = userAns === q.correct_option;
    const domainName = DOMAIN_NAMES[q.domain] || q.domain;

    container.innerHTML = `
      <div class="card">
        <div class="exam-status-bar">
          <div>
            <span style="font-weight: 700; font-size: 1.05rem; color: var(--primary);">
              Review Item ${state.psi.reviewCurrentPos + 1}
            </span>
            <span style="color: var(--text-muted); font-size: 0.95rem;">
              of ${state.psi.reviewIndices.length} (${state.psi.reviewFilter === 'missed' ? 'Missed Only' : 'All Items'})
            </span>
          </div>
          <div>
            <button class="btn btn-sm btn-secondary" onclick="state.psi.status = 'results'; render();">
              &larr; Back to Score Report
            </button>
          </div>
        </div>

        <div style="display: flex; gap: 0.4rem; margin-bottom: 0.75rem;">
          <span class="badge badge-primary">${escapeHtml(domainName)}</span>
          <span class="badge ${isCorrect ? 'badge-success' : 'badge-danger'}">
            ${isCorrect ? '✓ Correct' : '✗ Incorrect'}
          </span>
          ${q.subtopic ? `<span class="badge">${escapeHtml(q.subtopic)}</span>` : ''}
        </div>

        <div class="question-prompt">${escapeHtml(q.question_text)}</div>

        <div class="options-list">
          ${["A", "B", "C", "D"].map(letter => {
            const isTarget = letter === q.correct_option;
            const isUser = letter === userAns;
            let optClass = '';
            if (isTarget) optClass = 'correct';
            else if (isUser && !isCorrect) optClass = 'incorrect';

            return `
              <div class="option-btn ${optClass}" style="cursor: default;">
                <span class="option-letter">${letter}</span>
                <span class="option-text">
                  ${escapeHtml(q.options[letter])}
                  ${isTarget ? ' <strong style="color: var(--success);">&bull; Correct Answer</strong>' : ''}
                  ${isUser && !isTarget ? ' <strong style="color: var(--danger);">&bull; Your Selection</strong>' : ''}
                  ${isUser && isTarget ? ' <strong style="color: var(--success);">&bull; Your Selection</strong>' : ''}
                </span>
              </div>
            `;
          }).join('')}
        </div>

        <div class="feedback-box ${isCorrect ? 'is-correct' : 'is-incorrect'}">
          <div class="feedback-status ${isCorrect ? 'correct' : 'incorrect'}">
            ${isCorrect ? '✓ Correct' : `✗ Incorrect (You selected ${userAns || 'None'})`}
          </div>
          <div class="citation-line">Legal Citation: ${escapeHtml(q.source_citation)}</div>
          <div class="explanation-text">${escapeHtml(q.explanation)}</div>
        </div>

        <div class="actions-footer">
          <div class="actions-group">
            <button class="btn btn-secondary" onclick="psiReviewPrev()" ${state.psi.reviewCurrentPos === 0 ? 'disabled' : ''}>
              &larr; Previous [P]
            </button>
            <button class="btn btn-secondary" onclick="psiReviewNext()" ${state.psi.reviewCurrentPos === state.psi.reviewIndices.length - 1 ? 'disabled' : ''}>
              Next [N] &rarr;
            </button>
          </div>
          <div>
            <button class="btn btn-primary" onclick="state.psi.status = 'results'; render();">
              Finish Review
            </button>
          </div>
        </div>
      </div>
    `;
    return;
  }
}

function renderDrill(container) {
  if (state.drill.questions.length === 0) {
    initDrillQuestions();
  }

  const currentQ = state.drill.questions[state.drill.currentIndex];
  if (!currentQ) {
    container.innerHTML = `
      <div class="card empty-state" style="max-width: 650px; margin: 2rem auto;">
        <h3>No Questions Available</h3>
        <p>No questions found matching the selected domain filter.</p>
        <button class="btn btn-primary" onclick="setDrillDomain('all')">View All Domains</button>
      </div>
    `;
    return;
  }

  const answeredChoice = state.drill.answered[currentQ.id];
  const isAnswered = answeredChoice !== undefined;
  const isCorrect = isAnswered && answeredChoice === currentQ.correct_option;
  const domainName = currentQ ? (DOMAIN_NAMES[currentQ.domain] || currentQ.domain) : '';

  container.innerHTML = `
    <div>
      <div class="domain-filters-bar">
        <button class="filter-btn ${state.drill.domain === 'all' ? 'active' : ''}" onclick="setDrillDomain('all')">
          All Domains (${QUESTION_BANK.length})
        </button>
        ${Object.entries(DOMAIN_NAMES).map(([dom, name]) => {
          const count = QUESTION_BANK.filter(q => q.domain === dom).length;
          return `
            <button class="filter-btn ${state.drill.domain === dom ? 'active' : ''}" onclick="setDrillDomain('${dom}')">
              ${escapeHtml(name)} (${count})
            </button>
          `;
        }).join('')}
      </div>

      <div class="card">
        <div class="exam-status-bar">
          <div>
            <span style="font-weight: 700; font-size: 1.05rem; color: var(--primary);">
              Drill Item ${state.drill.currentIndex + 1}
            </span>
            <span style="color: var(--text-muted); font-size: 0.95rem;">
              of ${state.drill.questions.length}
            </span>
          </div>
          <div class="actions-group">
            <button class="btn btn-sm ${state.drill.shuffled ? 'btn-primary' : 'btn-outline'}" onclick="toggleDrillShuffle()">
              🔀 Shuffle: ${state.drill.shuffled ? 'ON' : 'OFF'}
            </button>
          </div>
        </div>

        <div style="display: flex; gap: 0.4rem; margin-bottom: 0.75rem;">
          <span class="badge badge-primary">${escapeHtml(domainName)}</span>
          ${currentQ.subtopic ? `<span class="badge">${escapeHtml(currentQ.subtopic)}</span>` : ''}
          <span class="badge">Item #${currentQ.id}</span>
        </div>

        <div class="question-prompt">${escapeHtml(currentQ.question_text)}</div>

        <div class="options-list">
          ${["A", "B", "C", "D"].map(letter => {
            let optClass = '';
            if (isAnswered) {
              if (letter === currentQ.correct_option) optClass = 'correct';
              else if (letter === answeredChoice) optClass = 'incorrect';
            }

            return `
              <button class="option-btn ${optClass}" onclick="selectDrillOption('${letter}')" ${isAnswered ? 'disabled' : ''}>
                <span class="option-letter">${letter}</span>
                <span class="option-text">${escapeHtml(currentQ.options[letter])}</span>
              </button>
            `;
          }).join('')}
        </div>

        ${isAnswered ? `
          <div class="feedback-box ${isCorrect ? 'is-correct' : 'is-incorrect'}">
            <div class="feedback-status ${isCorrect ? 'correct' : 'incorrect'}">
              ${isCorrect ? '✓ Correct!' : `✗ Incorrect (Correct answer is Option ${currentQ.correct_option})`}
            </div>
            <div class="citation-line">Legal Citation: ${escapeHtml(currentQ.source_citation)}</div>
            <div class="explanation-text">${escapeHtml(currentQ.explanation)}</div>
          </div>
        ` : ''}

        <div class="actions-footer">
          <div class="actions-group">
            <button class="btn btn-secondary" onclick="drillPrev()" ${state.drill.currentIndex === 0 ? 'disabled' : ''}>
              &larr; Previous [P]
            </button>
            <button class="btn ${isAnswered ? 'btn-primary' : 'btn-secondary'}" onclick="drillNext()" ${state.drill.currentIndex === state.drill.questions.length - 1 ? 'disabled' : ''}>
              Next [N / Enter] &rarr;
            </button>
          </div>
          <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">
            <span>Jump to:</span>
            <input type="number" min="1" max="${state.drill.questions.length}" value="${state.drill.currentIndex + 1}"
              style="width: 60px; padding: 0.3rem 0.4rem; border: 1px solid var(--border-color); border-radius: 4px; background: var(--card-bg); color: var(--text-primary);"
              onchange="drillJump(parseInt(this.value, 10) - 1)">
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderMissed(container) {
  initMissedQuestions();
  const list = state.missed.questions;

  if (list.length === 0) {
    container.innerHTML = `
      <div class="card empty-state" style="max-width: 650px; margin: 2rem auto;">
        <div style="font-size: 3rem; margin-bottom: 0.75rem;">🎉</div>
        <h3>No Missed Questions Saved</h3>
        <p>Your local remediation queue is completely clean! Whenever you miss an item during a <strong>PSI Exam Simulation</strong> or <strong>Domain Study Drill</strong>, it will automatically appear here for focused review.</p>
        <div style="display: flex; justify-content: center; gap: 0.75rem;">
          <button class="btn btn-primary" onclick="switchMode('psi')">Take PSI Simulation</button>
          <button class="btn btn-secondary" onclick="switchMode('drill')">Practice Domain Drill</button>
        </div>
      </div>
    `;
    return;
  }

  const currentQ = list[state.missed.currentIndex];
  const answeredChoice = currentQ ? state.missed.answered[currentQ.id] : null;
  const isAnswered = answeredChoice !== undefined;
  const isCorrect = isAnswered && answeredChoice === currentQ.correct_option;
  const domainName = currentQ ? (DOMAIN_NAMES[currentQ.domain] || currentQ.domain) : '';

  container.innerHTML = `
    <div class="card">
      <div class="exam-status-bar">
        <div>
          <span style="font-weight: 700; font-size: 1.05rem; color: var(--danger);">
            Missed Queue: Question ${state.missed.currentIndex + 1}
          </span>
          <span style="color: var(--text-muted); font-size: 0.95rem;">
            of ${list.length}
          </span>
        </div>
        <div class="actions-group">
          <button class="btn btn-sm btn-outline" onclick="removeCurrentMissed(${currentQ.id})" title="Remove this question from missed queue once mastered">
            ✓ Mastered (Remove)
          </button>
          <button class="btn btn-sm btn-danger" onclick="handleClearAllMissed()">
            Clear All
          </button>
        </div>
      </div>

      <div style="display: flex; gap: 0.4rem; margin-bottom: 0.75rem;">
        <span class="badge badge-primary">${escapeHtml(domainName)}</span>
        ${currentQ.subtopic ? `<span class="badge">${escapeHtml(currentQ.subtopic)}</span>` : ''}
        <span class="badge badge-warning">Missed Item #${currentQ.id}</span>
      </div>

      <div class="question-prompt">${escapeHtml(currentQ.question_text)}</div>

      <div class="options-list">
        ${["A", "B", "C", "D"].map(letter => {
          let optClass = '';
          if (isAnswered) {
            if (letter === currentQ.correct_option) optClass = 'correct';
            else if (letter === answeredChoice) optClass = 'incorrect';
          }

          return `
            <button class="option-btn ${optClass}" onclick="selectMissedOption('${letter}')" ${isAnswered ? 'disabled' : ''}>
              <span class="option-letter">${letter}</span>
              <span class="option-text">${escapeHtml(currentQ.options[letter])}</span>
            </button>
          `;
        }).join('')}
      </div>

      ${isAnswered ? `
        <div class="feedback-box ${isCorrect ? 'is-correct' : 'is-incorrect'}">
          <div class="feedback-status ${isCorrect ? 'correct' : 'incorrect'}">
            ${isCorrect ? '✓ Correct! Great job!' : `✗ Incorrect (Correct answer is Option ${currentQ.correct_option})`}
          </div>
          <div class="citation-line">Legal Citation: ${escapeHtml(currentQ.source_citation)}</div>
          <div class="explanation-text">${escapeHtml(currentQ.explanation)}</div>
        </div>
      ` : ''}

      <div class="actions-footer">
        <div class="actions-group">
          <button class="btn btn-secondary" onclick="missedPrev()" ${state.missed.currentIndex === 0 ? 'disabled' : ''}>
            &larr; Previous [P]
          </button>
          <button class="btn ${isAnswered ? 'btn-primary' : 'btn-secondary'}" onclick="missedNext()" ${state.missed.currentIndex === list.length - 1 ? 'disabled' : ''}>
            Next [N / Enter] &rarr;
          </button>
        </div>
        <div>
          ${isCorrect ? `
            <button class="btn btn-sm btn-primary" onclick="removeCurrentMissed(${currentQ.id})">
              ✓ Remove from Queue &amp; Continue
            </button>
          ` : ''}
        </div>
      </div>
    </div>
  `;
}

// INITIALIZATION
window.addEventListener('beforeunload', (e) => {
  if (state.mode === 'psi' && state.psi.status === 'active') {
    e.preventDefault();
    e.returnValue = '';
  }
});

window.addEventListener('DOMContentLoaded', () => {
  initTheme();
  updateMissedBadge();
  render();
});
</script>
</body>
</html>
"""


def generate_web_quizzer(
    output_path: Path,
    pool_path: Path | None = None,
) -> Path:
    """Generate self-contained standalone HTML5 quizzer application.

    Embeds all 435 curated questions with JSON, pure native responsive CSS (light/dark mode),
    and a JavaScript engine supporting PSI Exam Simulation (50 items matching quotas, 60-min timer,
    5x10 jump grid, 38/50 pass scoring, review mode), Domain Study Drill (instant green/red feedback,
    statutory citations, explanations), and Missed Questions drill with browser localStorage persistence.
    """
    if pool_path is None:
        repo_root = Path(__file__).resolve().parent.parent
        pool_path = repo_root / "gamb_exam" / "question_pool.json"

    with pool_path.open("r", encoding="utf-8") as f:
        questions: list[dict[str, Any]] = json.load(f)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    questions_json = json.dumps(questions, indent=2, ensure_ascii=False)
    # Prevent closing script tag injection case-insensitively
    questions_json = re.sub(r"(?i)</script>", r"<\\/script>", questions_json)

    domain_names_json = re.sub(
        r"(?i)</script>",
        r"<\\/script>",
        json.dumps(DOMAIN_DISPLAY_NAMES, ensure_ascii=False),
    )
    domain_quotas_json = re.sub(
        r"(?i)</script>",
        r"<\\/script>",
        json.dumps(DOMAIN_QUOTAS, ensure_ascii=False),
    )

    rendered_html = (
        WEB_QUIZZER_HTML_TEMPLATE
        .replace("__QUESTION_BANK_JSON__", questions_json)
        .replace("__DOMAIN_DISPLAY_NAMES_JSON__", domain_names_json)
        .replace("__DOMAIN_QUOTAS_JSON__", domain_quotas_json)
        .replace("__LEGAL_DISCLAIMER__", html.escape(LEGAL_DISCLAIMER))
    )

    output_path.write_text(rendered_html, encoding="utf-8")
    return output_path


def build_all_assets(
    output_dir: Path | str,
    pool_path: Path | str | None = None,
) -> dict[str, list[Path]]:
    """Coordinate full generation of all consumer study products.

    Creates subdirectories under `output_dir`:
    - `pdfs/`:
        - `GAMB_Statutory_Cheat_Sheet.pdf`
        - `GAMB_435_Question_Compendium.pdf`
        - `GAMB_Practice_Exam_Form_A.pdf`
        - `GAMB_Practice_Exam_Form_B.pdf`
        - `GAMB_Practice_Exam_Form_C.pdf`
    - `docs/study_materials/`:
        - `cheat_sheet.md`
        - `compendium_questions.md`
        - `compendium_key.md`
        - `practice_exam_form_a.md`
        - `practice_exam_form_b.md`
        - `practice_exam_form_c.md`
    - `web/`:
        - `index.html`

    Args:
        output_dir: Root directory where output directories (pdfs, docs, web) will be created.
        pool_path: Optional path to questions pool JSON file.

    Returns:
        Dict mapping asset category ("pdfs", "docs", "web") to list of generated Path objects.
    """
    out_dir = Path(output_dir)
    repo_root = Path(__file__).resolve().parent.parent
    pool_file = Path(pool_path) if pool_path is not None else repo_root / "gamb_exam" / "question_pool.json"

    pdfs_dir = out_dir / "pdfs"
    docs_dir = out_dir / "docs" / "study_materials"
    web_dir = out_dir / "web"

    pdfs_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    web_dir.mkdir(parents=True, exist_ok=True)

    # 1. Cheat Sheet
    cheat_sheet_md = docs_dir / "cheat_sheet.md"
    cheat_sheet_html = docs_dir / "cheat_sheet.html"
    cheat_sheet_pdf = pdfs_dir / "GAMB_Statutory_Cheat_Sheet.pdf"
    generate_cheat_sheet(md_path=cheat_sheet_md, html_path=cheat_sheet_html)
    compile_html_to_pdf(cheat_sheet_html, cheat_sheet_pdf)
    if cheat_sheet_html.exists():
        cheat_sheet_html.unlink()

    # 2. Compendium
    compendium_q_md = docs_dir / "compendium_questions.md"
    compendium_k_md = docs_dir / "compendium_key.md"
    compendium_html = docs_dir / "compendium.html"
    compendium_pdf = pdfs_dir / "GAMB_435_Question_Compendium.pdf"
    generate_compendium(
        q_md=compendium_q_md,
        k_md=compendium_k_md,
        html_path=compendium_html,
        pool_path=pool_file,
    )
    compile_html_to_pdf(compendium_html, compendium_pdf)
    if compendium_html.exists():
        compendium_html.unlink()

    # 3. Practice Forms A, B, C
    forms = generate_practice_forms(
        md_dir=docs_dir,
        pdf_dir=pdfs_dir,
        pool_path=pool_file,
    )

    # 4. Web Quizzer
    web_index = web_dir / "index.html"
    generate_web_quizzer(output_path=web_index, pool_path=pool_file)

    return {
        "pdfs": [
            cheat_sheet_pdf,
            compendium_pdf,
            forms["A"]["pdf_path"],
            forms["B"]["pdf_path"],
            forms["C"]["pdf_path"],
        ],
        "docs": [
            cheat_sheet_md,
            compendium_q_md,
            compendium_k_md,
            forms["A"]["md_path"],
            forms["B"]["md_path"],
            forms["C"]["md_path"],
        ],
        "web": [
            web_index,
        ],
    }

