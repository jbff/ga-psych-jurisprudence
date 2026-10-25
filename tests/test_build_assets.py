import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from gamb_exam.build_assets import (
    compile_html_to_pdf,
    generate_cheat_sheet,
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

    html_content = html_path.read_text(encoding="utf-8")
    assert "Georgia Psychology Jurisprudence Examination" in html_content
    assert "Statutory Quick-Reference Cheat Sheet" in html_content
    assert "O.C.G.A. § 19-7-5" in html_content
    assert "O.C.G.A. § 43-39-16" in html_content
    assert "40 hours" in html_content

    # Test PDF compilation
    compile_html_to_pdf(html_path, pdf_path)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 5000  # Non-trivial PDF size


def test_compile_html_to_pdf_missing_source(tmp_path: Path):
    nonexistent = tmp_path / "missing.html"
    out_pdf = tmp_path / "output.pdf"
    with pytest.raises(FileNotFoundError, match="HTML source file not found"):
        compile_html_to_pdf(nonexistent, out_pdf)


def test_compile_html_to_pdf_cli_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    html_file = tmp_path / "test.html"
    html_file.write_text("<p>Hello</p>", encoding="utf-8")
    out_pdf = tmp_path / "output.pdf"

    monkeypatch.setattr("shutil.which", lambda bin_name: "/usr/bin/weasyprint")

    mock_res = MagicMock()
    mock_res.returncode = 1
    mock_res.stderr = "Fatal PDF generation error"
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_res)

    with pytest.raises(RuntimeError, match="WeasyPrint failed \\(1\\): Fatal PDF generation error"):
        compile_html_to_pdf(html_file, out_pdf)


def test_compile_html_to_pdf_no_weasyprint(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    html_file = tmp_path / "test.html"
    html_file.write_text("<p>Hello</p>", encoding="utf-8")
    out_pdf = tmp_path / "output.pdf"

    monkeypatch.setattr("shutil.which", lambda bin_name: None)
    monkeypatch.setattr("builtins.__import__", MagicMock(side_effect=ImportError("No module named weasyprint")))

    with pytest.raises(RuntimeError, match="Neither weasyprint CLI binary nor weasyprint Python package is available"):
        compile_html_to_pdf(html_file, out_pdf)


def test_compile_html_to_pdf_python_api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    html_file = tmp_path / "test.html"
    html_file.write_text("<p>Hello</p>", encoding="utf-8")
    out_pdf = tmp_path / "output.pdf"

    monkeypatch.setattr("shutil.which", lambda bin_name: None)

    mock_weasyprint = MagicMock()
    monkeypatch.setitem(__import__("sys").modules, "weasyprint", mock_weasyprint)

    compile_html_to_pdf(html_file, out_pdf)
    mock_weasyprint.HTML.assert_called_once_with(filename=str(html_file))
    mock_weasyprint.HTML.return_value.write_pdf.assert_called_once_with(str(out_pdf))


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


def test_generate_compendium_html_escaping(tmp_path: Path):
    mock_pool = tmp_path / "mock_pool.json"
    mock_pool.write_text(
        json.dumps([
            {
                "id": 1,
                "domain": "prof-relationships",
                "question_text": "Is <script>alert('xss')</script> allowed & safe?",
                "options": {
                    "A": "No <tag> & unsafe",
                    "B": "Yes > No",
                    "C": "Option \"C\"",
                    "D": "Option 'D'",
                },
                "correct_option": "A",
                "source_citation": "Rule 510-4 & O.C.G.A. § 16-6-5.1 <Statute>",
                "explanation": "Must escape <elements> & entities.",
            }
        ]),
        encoding="utf-8",
    )
    q_md = tmp_path / "q.md"
    k_md = tmp_path / "k.md"
    html_path = tmp_path / "out.html"

    generate_compendium(q_md=q_md, k_md=k_md, html_path=html_path, pool_path=mock_pool)

    html_content = html_path.read_text(encoding="utf-8")
    assert "<script>alert('xss')</script>" not in html_content
    assert "&lt;script&gt;" in html_content
    assert "&lt;tag&gt; &amp; unsafe" in html_content
    assert "Yes &gt; No" in html_content
    assert "&lt;Statute&gt;" in html_content
    assert "&lt;elements&gt; &amp; entities." in html_content


def test_generate_practice_forms(tmp_path: Path):
    forms = generate_practice_forms(output_dir=tmp_path)
    assert len(forms) == 3
    assert set(forms.keys()) == {"A", "B", "C"}

    repo_root = Path(__file__).resolve().parent.parent
    with (repo_root / "gamb_exam" / "question_pool.json").open("r", encoding="utf-8") as f:
        pool_by_id = {q["id"]: q for q in json.load(f)}

    for letter, data in forms.items():
        assert letter in ["A", "B", "C"]
        assert len(data["questions"]) == 50
        # Check quota
        domain_counts: dict[str, int] = {}
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
        # Check option shuffling correctness: correct answer text must be preserved
        for q in data["questions"]:
            orig_q = pool_by_id[q["id"]]
            orig_correct_text = orig_q["options"][orig_q["correct_option"]].strip()
            new_correct_text = q["options"][q["correct_option"]].strip()
            assert orig_correct_text == new_correct_text

        # Check files created
        assert (tmp_path / f"practice_exam_form_{letter.lower()}.md").exists()
        assert (tmp_path / f"practice_exam_form_{letter.lower()}.html").exists()
        pdf_path = tmp_path / f"GAMB_Practice_Exam_Form_{letter}.pdf"
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 30000

    # Ensure Forms A, B, and C have distinct question selections
    ids_a = {q["id"] for q in forms["A"]["questions"]}
    ids_b = {q["id"] for q in forms["B"]["questions"]}
    ids_c = {q["id"] for q in forms["C"]["questions"]}
    assert ids_a != ids_b
    assert ids_b != ids_c


def test_generate_practice_forms_insufficient_questions(tmp_path: Path):
    empty_pool = tmp_path / "empty_pool.json"
    empty_pool.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="Insufficient questions in domain"):
        generate_practice_forms(output_dir=tmp_path, pool_path=empty_pool)


def test_generate_practice_forms_html_escaping(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Mock compile_html_to_pdf to avoid heavy weasyprint rendering in unit test
    monkeypatch.setattr("gamb_exam.build_assets.compile_html_to_pdf", lambda src, dst: dst.touch())

    quotas = {
        "prof-relationships": 14,
        "licensure": 13,
        "competence": 9,
        "assessment": 6,
        "privacy": 5,
        "recordkeeping": 3,
    }
    mock_items = []
    item_id = 1
    for domain, count in quotas.items():
        for i in range(count):
            if item_id == 1:
                q_text = "Is <script>alert('xss')</script> valid & safe?"
                opt_a = "No <unsafe> & invalid"
                citation = "Rule 510-4 <Statute> & § 43-39"
                explanation = "Must escape <b>bold</b> & special characters."
            else:
                q_text = f"Sample question {item_id} for {domain}?"
                opt_a = "Correct answer"
                citation = f"Rule 510-{item_id}"
                explanation = f"Explanation {item_id}"

            mock_items.append({
                "id": item_id,
                "domain": domain,
                "question_text": q_text,
                "options": {
                    "A": opt_a,
                    "B": "Option B > C",
                    "C": "Option C < D",
                    "D": "Option D & E",
                },
                "correct_option": "A",
                "source_citation": citation,
                "explanation": explanation,
            })
            item_id += 1

    mock_pool = tmp_path / "mock_escaped_pool.json"
    mock_pool.write_text(json.dumps(mock_items), encoding="utf-8")

    generate_practice_forms(output_dir=tmp_path, pool_path=mock_pool)

    html_file = tmp_path / "practice_exam_form_a.html"
    assert html_file.exists()
    content = html_file.read_text(encoding="utf-8")

    assert "<script>alert('xss')</script>" not in content
    assert "&lt;script&gt;" in content
    assert "valid &amp; safe?" in content
    assert "No &lt;unsafe&gt; &amp; invalid" in content
    assert "&lt;Statute&gt; &amp; § 43-39" in content
    assert "&lt;b&gt;bold&lt;/b&gt; &amp; special characters." in content


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


def test_generate_web_quizzer_custom_pool(tmp_path: Path):
    mock_pool = tmp_path / "mock_pool.json"
    mock_pool.write_text(
        json.dumps([
            {
                "id": 999,
                "domain": "licensure",
                "question_text": "Custom question?",
                "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                "correct_option": "B",
                "source_citation": "Rule 510-2-.01",
                "explanation": "Custom explanation.",
            }
        ]),
        encoding="utf-8",
    )
    web_file = tmp_path / "nested" / "quizzer.html"
    generate_web_quizzer(output_path=web_file, pool_path=mock_pool)

    assert web_file.exists()
    content = web_file.read_text(encoding="utf-8")
    assert '"id": 999' in content
    assert "Custom question?" in content






