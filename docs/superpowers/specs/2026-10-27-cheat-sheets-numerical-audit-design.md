# Design Specification: Georgia Psychology Jurisprudence Examination (GAMB) Cheat Sheets & Numerical Audit

**Date:** 2026-10-27  
**Status:** Approved  
**Author:** Antigravity / John B. Fleming, PhD  

---

## 1. Overview & Objective
An audit of the Georgia Psychology Jurisprudence Examination study aids against the primary statutory corpus (O.C.G.A. Title 43 Ch. 39, Title 37 Ch. 3, Title 19 Ch. 7, Title 30 Ch. 5, Title 16 Ch. 6, Title 16 Ch. 13) and Board Rules (Rules Chapter 510) revealed that several critical numerical deadlines and timeframes tested on the exam were omitted from the quick-reference materials.

To provide optimal study utility, the reference system is divided into two focused study aids:
1. **`GAMB_Statutory_Cheat_Sheet`**: A thematic, statutory reference sheet covering all major domains of Georgia law, regulations, ethics, reporting, and disciplinary procedures.
2. **`GAMB_Numbers_And_Deadlines_Cheat_Sheet`**: A dedicated chronological numbers cram sheet structured specifically for rapid memorization of statutory hours, days, months, years, supervision ratios, and board metrics.

Both aids are authored in Markdown and compiled into print-ready, high-resolution PDFs using WeasyPrint via the `gamb-exam build-assets` pipeline.

---

## 2. Content Specifications

### 2.1 Thematic Cheat Sheet (`cheat_sheet.md` / `GAMB_Statutory_Cheat_Sheet.pdf`)
* **Section 1: Licensure, Supervision, Examination & Continuing Education (Rules 510-2, 510-3, 510-8)**
  * Pre-doctoral internship: minimum 1,500 hours (or 2,000 hours under Rule 510-2-.05); 500 hours direct client contact.
  * Doctoral residency: minimum 1 year full-time or 540 in-person coursework hours (12 hrs/wk x 15 wks x 3 semesters).
  * Postdoctoral Supervised Work Experience (SWE): minimum 1,500 hours over 11 to 24 months; 500 direct client contact hours.
  * Supervision ratios: 1 hour individual supervision per 30 hours SWE; 1 hour per 20 hours face-to-face clinical service in general practice; maximum 3 supervisees concurrently without prior Board approval.
  * Examination retakes & remediation: failed GAMB re-examination wait period is 30 days; 3 EPPP failures require 3 semester hours or 15 CE hours; 6 EPPP failures require 9 semester hours or 45 CE hours.
  * Endorsement & Senior Psychologist: 10 years unblemished licensure for senior psychologist endorsement; 3 years continuous full-time practice (30 hrs/wk, 50 wks/yr) accepted as SWE equivalent.
  * Biennial CE requirements: 40 hours per biennium (ending Dec 31 of even years); minimum 6 hours professional ethics (Area I live); minimum 20 hours Area I live/interactive; maximum 16 hours Area II self-study.
  * License expiration & late renewal: expires Dec 31 of even years; 31-day late penalty period (Jan 1–31); CE audit cure period of 31 days.
* **Section 2: Emergency Commitment & Mandatory Reporting (O.C.G.A. §§ 37-3-41, 19-7-5, 30-5-4)**
  * Form 1013 involuntary examination certificate: requires personal examination within preceding 48 hours; valid for 7 days after execution; peace officer must execute custody within 72 hours of receiving certificate.
  * Court apprehension order: two affiants must have observed individual within preceding 48 hours; court apprehension order valid for 7 days.
  * Child abuse reporting: mandatory reporting immediately and no later than 24 hours from reasonable suspicion to DFCS or law enforcement; privilege abrogated; knowing failure to report is a misdemeanor; broad good-faith immunity.
  * Elder / disabled adult abuse reporting: mandatory reporting to Adult Protective Services (DHS) or law enforcement; law enforcement must forward report within 24 hours; privilege abrogated.
* **Section 3: Confidentiality, Privilege & Prohibited Relationships (O.C.G.A. §§ 43-39-16, 16-6-5.1, Rule 510-4)**
  * Evidentiary privilege: psychologist-client communications placed on identical legal footing as attorney-client privilege (O.C.G.A. § 43-39-16; § 24-5-501).
  * Sexual misconduct 1st degree: felony, 1 to 25 years imprisonment and fine up to $100,000 (10 to 30 years if victim < 16). Consent is not a defense.
  * Sexual misconduct 2nd degree: sexual contact without explicit penetration; high and aggravated misdemeanor (repeat conviction is felony 1 to 5 years).
  * Former client sexual relations: prohibited for at least 2 years post-termination (APA Standard 10.08 / Rule 510-4-.02).
* **Section 4: Practice Limits, Recordkeeping & Disciplinary Penalties (O.C.G.A. §§ 43-39, 43-1, 16-13, 50-13)**
  * Clinical record retention: adult records retained minimum 7 years from last date of service; minor records retained minimum 7 years past age of majority (age 25).
  * Out-of-state temporary practice: up to 30 days per calendar year with at least 5 days prior written notice to the Board; PSYPACT IPC up to 30 days per year.
  * Mandatory conviction reporting: licensee must notify Board within 10 days of any felony conviction or controlled substance conviction.
  * Board disciplinary penalties: civil fines up to $500 per violation; unlicensed practice punishable as misdemeanor ($100–$1,000 fine and/or up to 12 months jail).
  * Administrative appeals: judicial review filed in Superior Court of Fulton County under "any evidence" standard.

---

### 2.2 Numerical Cram Sheet (`numbers_cheat_sheet.md` / `GAMB_Numbers_And_Deadlines_Cheat_Sheet.pdf`)
* **Table 1: The Clock — Hours**
  * 24 Hours: Child abuse reporting deadline; Law enforcement elder abuse forwarding deadline.
  * 48 Hours: Form 1013 personal examination window; Court 1013 apprehension petition affiant observation window.
  * 72 Hours: Peace officer execution window after receiving Form 1013 certificate.
* **Table 2: The Calendar — Days**
  * 5 Days: Advance written notice to Board for out-of-state temporary practice.
  * 7 Days: Validity / expiration of Form 1013 emergency certificate and Court apprehension order.
  * 10 Days: Mandatory notification to Board of felony conviction or drug conviction.
  * 30 Days: Re-examination waiting period after failing GAMB; Deadline to respond to Board request for additional application info; Mandatory reporting of out-of-state license surrender or discipline; Maximum temporary out-of-state practice per calendar year; Maximum PSYPACT IPC temporary practice per calendar year.
  * 31 Days: Late renewal penalty period (January 1–31 following Dec 31 even-year expiration); CE audit compliance cure window.
  * 60 Days: Deadline to petition Board for reconsideration following denial of provisional license / endorsement.
  * 120 Days: Maximum effective duration of emergency Board rules.
* **Table 3: Months & Years**
  * 6 Months: Maximum age of work sample submitted for Oral Examination; Validity of temporary volunteer license.
  * 11 to 24 Months: Mandatory duration window to complete 1,500 hours of postdoctoral SWE or internship.
  * 12 Months (1 Year): Validity of temporary psychology license; Maximum period to reinstate lapsed license without retaking exams; Maximum imprisonment for unlicensed practice misdemeanor.
  * 24 Months (2 Years): Validity of provisional psychology license; Biennial license renewal and CE reporting cycle; APA prohibition on sexual intimacies with former clients.
  * 3 Years: Out-of-state practice equivalency accepted in lieu of SWE (30 hrs/wk, 50 wks/yr).
  * 5 Years: Statutory term length of Georgia Psychology Board members.
  * 7 Years / Age 25: Minimum clinical record retention period for adults (7 years) and minors (7 years past age 18 = age 25).
  * 10 Years: Practice duration required to qualify for Senior Psychologist licensure by endorsement.
* **Table 4: Hours, Supervision Ratios & Passing Standards**
  * Supervision: 1 hour per 30 hours SWE; 1 hour per 20 hours clinical face-to-face; Maximum 3 supervisees concurrently.
  * Hour Milestones: 40 CE hours per biennium; 6 CE hours ethics; minimum 20 Area I; maximum 16 Area II; 1,500 internship hours; 1,500 SWE hours; 500 direct client contact hours; 540 in-person doctoral residency coursework hours.
  * Remediation: 3 EPPP failures → 3 semester hours or 15 CE hours; 6 EPPP failures → 9 semester hours or 45 CE hours.
  * Board Metrics & Passing: 6 Board members (5 psychologists + 1 consumer); Quorum of 4 members. Passing scores: 75% on GAMB Jurisprudence; 75% on Oral Examination; 500 scaled on EPPP Part 1 & 2. Fines: $500 max civil fine per violation.

---

## 3. Architecture & Build Pipeline Integration
* **Module:** `gamb_exam/build_assets.py`
  * Add `generate_numbers_cheat_sheet(md_path: Path, html_path: Path) -> None`
  * Enhance `generate_cheat_sheet(md_path: Path, html_path: Path) -> None`
  * Update `build_all_assets()` to generate both Markdown documents and invoke `compile_html_to_pdf()` to compile both PDFs:
    * `docs/study_materials/cheat_sheet.md` → `pdfs/GAMB_Statutory_Cheat_Sheet.pdf`
    * `docs/study_materials/numbers_cheat_sheet.md` → `pdfs/GAMB_Numbers_And_Deadlines_Cheat_Sheet.pdf`
* **CLI:** `gamb-exam build-assets` builds all materials including the new numbers sheet.
* **Testing:**
  * `tests/test_build_assets.py`: Verify both generators create valid markdown and HTML with all targeted keywords and numbers.
  * `tests/test_cli.py`: Verify CLI build command outputs both files and PDFs without error.
