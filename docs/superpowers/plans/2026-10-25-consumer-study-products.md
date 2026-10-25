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

- [x] **Step 1: Write failing test for cheat sheet generation**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `compile_html_to_pdf` and `generate_cheat_sheet` in `gamb_exam/build_assets.py`**
- [x] **Step 4: Run test to verify it passes**
- [x] **Step 5: Commit**

---

### Task 2: Full 435-Question Domain Compendium (Booklet & Back-of-Book Key)

**Files:**
- Modify: `gamb_exam/build_assets.py`
- Modify: `tests/test_build_assets.py`
- Output: `pdfs/GAMB_435_Question_Compendium.pdf`
- Output: `docs/study_materials/compendium_questions.md`
- Output: `docs/study_materials/compendium_key.md`

- [x] **Step 1: Write failing test for compendium generation**

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

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_build_assets.py::test_generate_compendium -v`  
Expected: FAIL (`ImportError: cannot import name 'generate_compendium'`).

- [x] **Step 3: Implement `generate_compendium` in `gamb_exam/build_assets.py`**

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

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_build_assets.py::test_generate_compendium -v`  
Expected: PASS.

- [x] **Step 5: Commit**

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

- [x] **Step 1: Write failing test for practice exam forms generation**

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

- [x] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_build_assets.py::test_generate_practice_forms -v`  
Expected: FAIL (`ImportError: cannot import name 'generate_practice_forms'`).

- [x] **Step 3: Implement `generate_practice_forms` in `gamb_exam/build_assets.py`**

In `gamb_exam/build_assets.py`:
- Use seeds 101 (Form A), 202 (Form B), 303 (Form C).
- Ingest `gamb_exam/question_pool.json`, group by domain, sample exact quotas with seeded `random.Random(seed)`.
- Generate for each form:
  - Instructions cover: 60-minute time limit, 50 questions, 38/50 (76%) pass cutoff, scoring sheet.
  - Section 1: Questions 1 to 50 with options A–D (no answers shown).
  - Section 2: Self-Scoring Bubble Sheet grid.
  - Section 3: Answer Key & Detailed Legal Citations in back.
- Compile to vector PDF using `compile_html_to_pdf`.

- [x] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_build_assets.py::test_generate_practice_forms -v`  
Expected: PASS.

- [x] **Step 5: Commit**

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
