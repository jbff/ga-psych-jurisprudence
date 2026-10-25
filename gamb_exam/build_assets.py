"""Asset generation pipeline for Georgia Psychology Jurisprudence Examination study products."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

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
