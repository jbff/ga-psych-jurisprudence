"""Unit tests for the CLI interface and entry points (gamb_exam.cli)."""

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from gamb_exam.db import (
    complete_session,
    create_session,
    init_db,
    insert_question,
    save_session_answer,
)


@pytest.fixture
def test_db_with_questions(tmp_db_path: Path) -> Path:
    """Fixture providing an initialized DB with sample questions across domains."""
    init_db(tmp_db_path)
    domains = [
        ("prof-relationships", 14),
        ("licensure", 13),
        ("competence", 9),
        ("assessment", 6),
        ("privacy", 5),
        ("recordkeeping", 3),
    ]
    q_id = 1
    for domain, count in domains:
        for _ in range(count):
            insert_question(
                {
                    "domain": domain,
                    "subtopic": "ethics",
                    "source_citation": "O.C.G.A. § 43-39-1",
                    "question_text": f"Question {q_id} in {domain}?",
                    "option_a": "Option A",
                    "option_b": "Option B",
                    "option_c": "Option C",
                    "option_d": "Option D",
                    "correct_option": "A",
                    "explanation": f"Explanation for question {q_id}",
                },
                db_path=tmp_db_path,
            )
            q_id += 1
    return tmp_db_path


def test_cli_help(capsys: pytest.CaptureFixture[str]):
    """Verifies --help returns exit code 0 and prints help description."""
    from gamb_exam.cli import main

    ret = main(["--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert (
        "gamb-exam" in captured.out
        or "Georgia Psychology Jurisprudence" in captured.out
    )


def test_cli_version(capsys: pytest.CaptureFixture[str]):
    """Verifies --version returns exit code 0 and prints version string."""
    from gamb_exam.cli import main

    ret = main(["--version"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "gamb-exam 1.0.0" in captured.out


def test_cli_no_args_prints_help(capsys: pytest.CaptureFixture[str]):
    """Verifies running main with no arguments displays help and returns 0."""
    from gamb_exam.cli import main

    ret = main([])
    assert ret == 0
    captured = capsys.readouterr()
    assert "gamb-exam" in captured.out or "usage:" in captured.out


def test_cli_test_command(tmp_db_path: Path):
    """Verifies main(['test']) calls generator and invokes ExamApp.run() with mode='timed_exam'."""
    from gamb_exam.cli import main

    mock_questions = [{"id": 1, "domain": "licensure", "question_text": "Sample"}]

    with (
        patch(
            "gamb_exam.cli.generate_exam_questions", return_value=mock_questions
        ) as mock_gen,
        patch("gamb_exam.tui.ExamApp") as mock_app_cls,
    ):
        mock_app_instance = MagicMock()
        mock_app_cls.return_value = mock_app_instance

        ret = main(["test", "--db", str(tmp_db_path), "--seed", "123", "--no-unseen"])
        assert ret == 0

        mock_gen.assert_called_once()
        gen_kwargs = mock_gen.call_args.kwargs
        assert gen_kwargs.get("prioritize_unseen") is False
        assert gen_kwargs.get("rng") is not None
        assert Path(gen_kwargs.get("db_path")) == tmp_db_path

        mock_app_cls.assert_called_once()
        app_kwargs = mock_app_cls.call_args.kwargs
        assert app_kwargs.get("questions") == mock_questions
        assert app_kwargs.get("mode") == "timed_exam"
        assert Path(app_kwargs.get("db_path")) == tmp_db_path
        mock_app_instance.run.assert_called_once()


def test_cli_test_command_unseeded_error(
    tmp_db_path: Path, capsys: pytest.CaptureFixture[str]
):
    """Verifies graceful error handling when DB is unseeded or missing."""
    from gamb_exam.cli import main

    with patch(
        "gamb_exam.cli.generate_exam_questions",
        side_effect=ValueError("Insufficient questions in domain 'licensure'"),
    ):
        ret = main(["test", "--db", str(tmp_db_path)])
        assert ret == 1
        captured = capsys.readouterr()
        assert "Error generating practice exam" in captured.out
        assert "Database may be missing or unseeded" in captured.out


def test_cli_study_command(test_db_with_questions: Path):
    """Verifies main(['study']) invokes ExamApp.run() with mode='study_drill'."""
    from gamb_exam.cli import main

    # Test unfiltered study command
    with patch("gamb_exam.tui.ExamApp") as mock_app_cls:
        mock_app_instance = MagicMock()
        mock_app_cls.return_value = mock_app_instance

        ret = main(["study", "--db", str(test_db_with_questions), "--count", "10"])
        assert ret == 0
        mock_app_cls.assert_called_once()
        app_kwargs = mock_app_cls.call_args.kwargs
        assert len(app_kwargs["questions"]) == 10
        assert app_kwargs["mode"] == "study_drill"
        mock_app_instance.run.assert_called_once()

    # Test domain-filtered study command
    with patch("gamb_exam.tui.ExamApp") as mock_app_cls:
        mock_app_instance = MagicMock()
        mock_app_cls.return_value = mock_app_instance

        ret = main(
            [
                "study",
                "--db",
                str(test_db_with_questions),
                "--domain",
                "licensure",
                "--count",
                "5",
            ]
        )
        assert ret == 0
        mock_app_cls.assert_called_once()
        app_kwargs = mock_app_cls.call_args.kwargs
        assert len(app_kwargs["questions"]) == 5
        assert all(q["domain"] == "licensure" for q in app_kwargs["questions"])
        assert app_kwargs["mode"] == "study_drill"
        mock_app_instance.run.assert_called_once()


def test_cli_study_command_shuffles(test_db_with_questions: Path):
    """Verifies unfiltered study command shuffles questions before slicing."""
    from gamb_exam.cli import main

    with (
        patch("random.shuffle") as mock_shuffle,
        patch("gamb_exam.tui.ExamApp") as mock_app_cls,
    ):
        mock_app_instance = MagicMock()
        mock_app_cls.return_value = mock_app_instance

        ret = main(["study", "--db", str(test_db_with_questions), "--count", "10"])
        assert ret == 0
        mock_shuffle.assert_called_once()


def test_cli_missed_command(tmp_db_path: Path, capsys: pytest.CaptureFixture[str]):
    """Verifies behavior when no missed questions exist vs when missed questions exist."""
    from gamb_exam.cli import main

    init_db(tmp_db_path)

    # 1. No missed questions
    with patch("gamb_exam.tui.ExamApp") as mock_app_cls:
        ret = main(["missed", "--db", str(tmp_db_path)])
        assert ret == 0
        mock_app_cls.assert_not_called()
        captured = capsys.readouterr()
        assert "No missed questions found" in captured.out

    # 2. Missed questions exist
    q_id = insert_question(
        {
            "domain": "licensure",
            "subtopic": "ethics",
            "source_citation": "Citation 1",
            "question_text": "Missed question?",
            "option_a": "A",
            "option_b": "B",
            "option_c": "C",
            "option_d": "D",
            "correct_option": "A",
            "explanation": "Exp",
        },
        db_path=tmp_db_path,
    )
    s_id = create_session(mode="timed_exam", db_path=tmp_db_path)
    save_session_answer(
        session_id=s_id,
        question_id=q_id,
        selected_option="B",
        is_correct=False,
        db_path=tmp_db_path,
    )

    with patch("gamb_exam.tui.ExamApp") as mock_app_cls:
        mock_app_instance = MagicMock()
        mock_app_cls.return_value = mock_app_instance

        ret = main(["missed", "--db", str(tmp_db_path)])
        assert ret == 0
        mock_app_cls.assert_called_once()
        app_kwargs = mock_app_cls.call_args.kwargs
        assert len(app_kwargs["questions"]) == 1
        assert app_kwargs["questions"][0]["id"] == q_id
        assert app_kwargs["mode"] == "study_drill"
        mock_app_instance.run.assert_called_once()


def test_cli_stats_command(tmp_db_path: Path, capsys: pytest.CaptureFixture[str]):
    """Verifies stats command when no sessions exist vs when history exists."""
    from gamb_exam.cli import main

    init_db(tmp_db_path)

    # 1. Empty state
    ret = main(["stats", "--db", str(tmp_db_path)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "No exam" in captured.out or "history" in captured.out.lower()

    # 2. Populated sessions: 1 passed, 1 failed, 1 incomplete
    s1 = create_session(mode="timed_exam", total_questions=50, db_path=tmp_db_path)
    complete_session(
        session_id=s1,
        score=40,
        percentage=80.0,
        passed=True,
        time_spent_seconds=1800,
        db_path=tmp_db_path,
    )

    s2 = create_session(mode="timed_exam", total_questions=50, db_path=tmp_db_path)
    complete_session(
        session_id=s2,
        score=35,
        percentage=70.0,
        passed=False,
        time_spent_seconds=2100,
        db_path=tmp_db_path,
    )

    # Incomplete session (never completed, passed=None)
    create_session(mode="timed_exam", total_questions=50, db_path=tmp_db_path)

    ret = main(["stats", "--db", str(tmp_db_path)])
    assert ret == 0
    captured = capsys.readouterr()
    # History table items
    assert "PASS" in captured.out
    assert "FAIL" in captured.out
    assert "INCOMPLETE" in captured.out
    assert "80.0%" in captured.out
    assert "70.0%" in captured.out
    # Summary line: 3 total, 2 completed, 1 passed -> 50.0% pass rate
    assert "Total exams: 3" in captured.out
    assert "Passing exams: 1" in captured.out
    assert "Pass rate: 50.0%" in captured.out
    assert "Average score: 75.0%" in captured.out


def test_cli_export_command(
    tmp_path: Path, test_db_with_questions: Path, capsys: pytest.CaptureFixture[str]
):
    """Verifies export subcommand generates markdown questions and key files."""
    from gamb_exam.cli import main

    export_dir = tmp_path / "mocks"
    ret = main(
        [
            "export",
            "--db",
            str(test_db_with_questions),
            "--output",
            str(export_dir),
            "--mock-id",
            "test1",
        ]
    )
    assert ret == 0

    assert (export_dir / "mock_test1_questions.md").exists()
    assert (export_dir / "mock_test1_key.md").exists()

    captured = capsys.readouterr()
    assert "mock_test1_questions.md" in captured.out
    assert "mock_test1_key.md" in captured.out


def test_cli_export_command_unseeded_error(
    tmp_db_path: Path, capsys: pytest.CaptureFixture[str]
):
    """Verifies graceful error handling on export when DB query fails."""
    from gamb_exam.cli import main

    with patch(
        "gamb_exam.cli.generate_exam_questions",
        side_effect=sqlite3.OperationalError("no such table: questions"),
    ):
        ret = main(["export", "--db", str(tmp_db_path)])
        assert ret == 1
        captured = capsys.readouterr()
        assert "Error exporting mock exam" in captured.out
        assert "Database may be missing or unseeded" in captured.out


def test_cli_keyboard_interrupt():
    """Verifies KeyboardInterrupt returns exit code 0 cleanly."""
    from gamb_exam.cli import main

    with (
        patch("gamb_exam.cli.generate_exam_questions", return_value=[{"id": 1}]),
        patch("gamb_exam.tui.ExamApp") as mock_app_cls,
    ):
        mock_app_instance = MagicMock()
        mock_app_instance.run.side_effect = KeyboardInterrupt()
        mock_app_cls.return_value = mock_app_instance

        ret = main(["test"])
        assert ret == 0


def test_build_assets_cli_help(capsys: pytest.CaptureFixture[str]):
    """Verifies main(['build-assets', '--help']) returns 0 and outputs expected text."""
    from gamb_exam.cli import main

    exit_code = main(["build-assets", "--help"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "build-assets" in captured.out
    assert "--output-dir" in captured.out


def test_build_assets_cli_execution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Verifies main(['build-assets', '--output-dir', ...]) generates all expected assets."""
    from gamb_exam.cli import main

    def mock_compile_html_to_pdf(html_path: Path, pdf_path: Path) -> None:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.touch()

    monkeypatch.setattr("gamb_exam.build_assets.compile_html_to_pdf", mock_compile_html_to_pdf)

    exit_code = main(["build-assets", "--output-dir", str(tmp_path)])
    assert exit_code == 0

    assert (tmp_path / "pdfs" / "GAMB_Statutory_Cheat_Sheet.pdf").exists()
    assert (tmp_path / "pdfs" / "GAMB_Numbers_And_Deadlines_Cheat_Sheet.pdf").exists()
    assert (tmp_path / "pdfs" / "GAMB_435_Question_Compendium.pdf").exists()
    assert (tmp_path / "pdfs" / "GAMB_Practice_Exam_Form_A.pdf").exists()
    assert (tmp_path / "pdfs" / "GAMB_Practice_Exam_Form_B.pdf").exists()
    assert (tmp_path / "pdfs" / "GAMB_Practice_Exam_Form_C.pdf").exists()
    assert (tmp_path / "docs" / "study_materials" / "cheat_sheet.md").exists()
    assert (tmp_path / "docs" / "study_materials" / "numbers_cheat_sheet.md").exists()
    assert (tmp_path / "docs" / "study_materials" / "compendium_questions.md").exists()
    assert (tmp_path / "docs" / "study_materials" / "compendium_key.md").exists()
    assert (tmp_path / "docs" / "study_materials" / "practice_exam_form_a.md").exists()
    assert (tmp_path / "web" / "index.html").exists()


def test_build_assets_cli_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    """Verifies main(['build-assets']) returns 1 on error and prints failure message."""
    from gamb_exam.cli import main

    monkeypatch.setattr(
        "gamb_exam.build_assets.build_all_assets",
        MagicMock(side_effect=RuntimeError("Disk full error")),
    )

    exit_code = main(["build-assets", "--output-dir", str(tmp_path)])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error building study assets: Disk full error" in captured.out

