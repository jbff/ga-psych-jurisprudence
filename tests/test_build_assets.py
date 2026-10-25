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
