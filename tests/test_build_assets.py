from pathlib import Path
from unittest.mock import MagicMock

import pytest

from gamb_exam.build_assets import compile_html_to_pdf, generate_cheat_sheet


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

