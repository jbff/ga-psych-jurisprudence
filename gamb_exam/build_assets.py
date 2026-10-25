"""Asset generation pipeline for Georgia Psychology Jurisprudence Examination study products."""

from __future__ import annotations

import html
import json
import shutil
import subprocess
from pathlib import Path

from gamb_exam.generator import DOMAIN_DISPLAY_NAMES, LEGAL_DISCLAIMER

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
    for d in questions_by_domain:
        questions_by_domain[d].sort(key=lambda x: x.get("id", 0))

    # Sequential numbering across the entire compendium (1..435)
    ordered_questions: list[tuple[int, dict]] = []
    q_counter = 1
    for domain in OFFICIAL_DOMAIN_ORDER:
        for q in questions_by_domain.get(domain, []):
            ordered_questions.append((q_counter, q))
            q_counter += 1

    # 1. Build Part I Markdown (compendium_questions.md)
    md_q_lines: list[str] = [
        "# Georgia Psychology Jurisprudence Examination (GAMB)",
        "## 435-Question Self-Study Compendium",
        "## Part I: Question Bank by Domain",
        "",
        LEGAL_DISCLAIMER,
        "",
        "---",
        "",
    ]

    for d_idx, domain in enumerate(OFFICIAL_DOMAIN_ORDER, 1):
        domain_title = DOMAIN_DISPLAY_NAMES.get(domain, domain)
        domain_desc = DOMAIN_DESCRIPTIONS.get(domain, "")
        domain_qs = [item for item in ordered_questions if item[1].get("domain") == domain]
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
        "## 435-Question Self-Study Compendium",
        "## Part II: Annotated Answer Key",
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
        "<title>GAMB 435-Question Domain Compendium</title>",
        f"<style>\n{PRINT_CSS}\n</style>",
        "</head>",
        "<body>",
        "<h1>Georgia Psychology Jurisprudence Examination (GAMB)</h1>",
        '<div class="badge">435-QUESTION SELF-STUDY COMPENDIUM</div>',
        "<h2>Part I: Question Bank by Domain</h2>",
        '<div class="disclaimer">',
        "<strong>LEGAL &amp; REGULATORY DISCLAIMER:</strong> This compendium is an independently authored study aid and is NOT official examination material from the Georgia State Board of Examiners of Psychologists or PSI Services LLC. Verified against O.C.G.A. and Board Rules Chapter 510.",
        "</div>",
    ]

    for d_idx, domain in enumerate(OFFICIAL_DOMAIN_ORDER, 1):
        domain_title = DOMAIN_DISPLAY_NAMES.get(domain, domain)
        domain_desc = DOMAIN_DESCRIPTIONS.get(domain, "")
        domain_qs = [item for item in ordered_questions if item[1].get("domain") == domain]
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
        '<div class="badge" style="font-size: 10pt; margin-top: 8pt; padding: 3pt 8pt;">QUESTIONS 1 &ndash; 435</div>',
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

