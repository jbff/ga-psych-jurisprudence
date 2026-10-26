"""Tests for the Terminal User Interface (TUI) Simulator (gamb_exam.tui)."""

from pathlib import Path

import pytest

from gamb_exam.db import get_connection, init_db, insert_question
from gamb_exam.tui import ExamApp


@pytest.fixture
def sample_questions() -> list[dict]:
    return [
        {
            "id": 1,
            "domain": "licensure",
            "subtopic": "Qualifications",
            "source_citation": "O.C.G.A. § 43-39-8",
            "question_text": "What is the minimum degree required for psychologist licensure in Georgia?",
            "option_a": "Master's degree",
            "option_b": "Doctoral degree",
            "option_c": "Bachelor's degree",
            "option_d": "Specialist degree",
            "correct_option": "B",
            "explanation": "O.C.G.A. § 43-39-8 requires a doctoral degree in psychology from an accredited institution.",
        },
        {
            "id": 2,
            "domain": "prof-relationships",
            "subtopic": "Dual Relationships",
            "source_citation": "Ga. Comp. R. & Regs. r. 510-4-.02",
            "question_text": "How many years must elapse before sexual intimacies with a former client?",
            "option_a": "1 year",
            "option_b": "2 years",
            "option_c": "5 years",
            "option_d": "Never permitted",
            "correct_option": "B",
            "explanation": "Rule 510-4-.02 prohibits sexual intimacies for at least 2 years post-termination.",
        },
        {
            "id": 3,
            "domain": "competence",
            "subtopic": "Continuing Education",
            "source_citation": "Ga. Comp. R. & Regs. r. 510-8-.01",
            "question_text": "How many CE hours are required per biennial renewal cycle?",
            "option_a": "20 hours",
            "option_b": "30 hours",
            "option_c": "40 hours",
            "option_d": "50 hours",
            "correct_option": "C",
            "explanation": "Psychologists must complete 40 CE hours every 2 years.",
        },
        {
            "id": 4,
            "domain": "privacy",
            "subtopic": "Privilege",
            "source_citation": "O.C.G.A. § 43-39-16",
            "question_text": "Confidential relations between psychologist and client are placed on the same basis as:",
            "option_a": "Doctor and patient",
            "option_b": "Attorney and client",
            "option_c": "Clergy and penitent",
            "option_d": "Spouses",
            "correct_option": "B",
            "explanation": "O.C.G.A. § 43-39-16 accords the psychologist-client privilege the same standing as attorney-client.",
        },
        {
            "id": 5,
            "domain": "recordkeeping",
            "subtopic": "Record Retention",
            "source_citation": "Ga. Comp. R. & Regs. r. 510-5-.06",
            "question_text": "How long must adult clinical records be maintained following termination?",
            "option_a": "3 years",
            "option_b": "5 years",
            "option_c": "7 years",
            "option_d": "10 years",
            "correct_option": "C",
            "explanation": "Board rules mandate retaining adult psychological records for at least 7 years.",
        },
    ]


@pytest.mark.asyncio
async def test_exam_app_init(sample_questions: list[dict]):
    """Test initial state of ExamApp upon instantiation."""
    app = ExamApp(questions=sample_questions, mode="timed_exam")
    assert app.current_index == 0
    assert app.time_remaining == 3600
    assert len(app.answers) == 0
    assert app.mode == "timed_exam"
    assert app.is_completed is False


@pytest.mark.asyncio
async def test_answer_selection_and_navigation(sample_questions: list[dict]):
    """Test selecting options via keystrokes and navigating back and forth."""
    app = ExamApp(questions=sample_questions, mode="timed_exam")
    async with app.run_test() as pilot:
        # Press 'a' to select option A on question 0
        # Press 'n' to advance to question 1
        # Press 'b' to select option B on question 1
        # Press 'p' to go back to question 0
        await pilot.press("a", "n", "b", "p")

        assert app.answers[0] == "A"
        assert app.answers[1] == "B"
        assert app.current_index == 0
        assert app.answers[0] == "A"

        # Test Enter key advances to next question
        await pilot.press("enter")
        assert app.current_index == 1


@pytest.mark.asyncio
async def test_flag_toggle_and_jump(sample_questions: list[dict]):
    """Test toggling question flags and toggling the jump grid view."""
    app = ExamApp(questions=sample_questions, mode="timed_exam")
    async with app.run_test() as pilot:
        # Initially not flagged
        assert 0 not in app.flags

        # Press 'f' toggles flag on
        await pilot.press("f")
        assert 0 in app.flags

        # Press 'f' toggles flag off
        await pilot.press("f")
        assert 0 not in app.flags

        # Press 'f' toggles flag on again
        await pilot.press("f")
        assert 0 in app.flags

        # Press 'j' toggles jump grid open/closed
        assert not app.jump_grid_open
        await pilot.press("j")
        assert app.jump_grid_open
        await pilot.press("j")
        assert not app.jump_grid_open


@pytest.mark.asyncio
async def test_submission_and_scoring(tmp_path: Path, sample_questions: list[dict]):
    """Test exam submission, score calculation (76% cutoff), and SQLite persistence."""
    db_file = tmp_path / "test_gamb.db"
    init_db(db_file)
    for q in sample_questions:
        insert_question(q, db_file)

    app = ExamApp(questions=sample_questions, mode="timed_exam", db_path=db_file)
    async with app.run_test() as pilot:
        # Answer Q0: 'B' (correct)
        await pilot.press("b")
        await pilot.press("n")

        # Answer Q1: 'B' (correct)
        await pilot.press("b")
        await pilot.press("n")

        # Answer Q2: 'C' (correct)
        await pilot.press("c")
        await pilot.press("n")

        # Answer Q3: 'B' (correct)
        await pilot.press("b")
        await pilot.press("n")

        # Answer Q4: 'A' (incorrect - correct is 'C')
        await pilot.press("a")

        # Submit exam (all 5 questions are answered, so pressing 's' submits directly)
        await pilot.press("s")

        assert app.is_completed is True
        assert app.score_data is not None
        assert app.score_data["total_correct"] == 4
        assert app.score_data["total_questions"] == 5
        assert app.score_data["percentage"] == 80.0
        assert app.score_data["passed"] is True  # 80.0% >= 76.0%

    # Verify database persistence
    conn = get_connection(db_file)
    try:
        session_row = conn.execute("SELECT * FROM exam_sessions WHERE id = ?", (app.session_id,)).fetchone()
        assert session_row is not None
        assert session_row["score"] == 4
        assert session_row["percentage"] == 80.0
        assert session_row["passed"] == 1
        assert session_row["mode"] == "timed_exam"
        assert session_row["time_spent_seconds"] >= 1

        answers = conn.execute(
            "SELECT * FROM session_answers WHERE session_id = ? ORDER BY id ASC", (app.session_id,)
        ).fetchall()
        assert len(answers) == 5
        # Verify 4 correct, 1 incorrect
        correct_count = sum(1 for a in answers if a["is_correct"] == 1)
        assert correct_count == 4
        # Verify each answered question recorded positive time spent
        for a in answers:
            assert a["time_spent_seconds"] >= 1
    finally:
        conn.close()


@pytest.mark.asyncio
async def test_study_drill_persistence_and_time_spent(tmp_path: Path, sample_questions: list[dict]):
    """Test that study_drill mode records accurate non-zero time_spent_seconds in database."""
    db_file = tmp_path / "test_gamb_drill.db"
    init_db(db_file)
    for q in sample_questions:
        insert_question(q, db_file)

    app = ExamApp(questions=sample_questions, mode="study_drill", db_path=db_file)
    async with app.run_test() as pilot:
        # Answer Q0: 'b'
        await pilot.press("b")
        await pilot.press("n")

        # Answer Q1: 'b'
        await pilot.press("b")
        await pilot.press("n")

        # Answer Q2: 'c'
        await pilot.press("c")

        # Force submit with unanswered remaining
        await pilot.press("s", "s")
        assert app.is_completed is True

    conn = get_connection(db_file)
    try:
        session_row = conn.execute("SELECT * FROM exam_sessions WHERE id = ?", (app.session_id,)).fetchone()
        assert session_row is not None
        assert session_row["mode"] == "study_drill"
        assert session_row["time_spent_seconds"] >= 1

        answers = conn.execute(
            "SELECT * FROM session_answers WHERE session_id = ? ORDER BY id ASC", (app.session_id,)
        ).fetchall()
        assert len(answers) == 5
        # Questions 0, 1, 2 were answered and should have time_spent_seconds >= 1
        assert answers[0]["time_spent_seconds"] >= 1
        assert answers[1]["time_spent_seconds"] >= 1
        assert answers[2]["time_spent_seconds"] >= 1
        # Questions 3, 4 were never visited, so should be 0
        assert answers[3]["time_spent_seconds"] == 0
        assert answers[4]["time_spent_seconds"] == 0
    finally:
        conn.close()


@pytest.mark.asyncio
async def test_study_drill_mode(sample_questions: list[dict]):
    """Test study drill mode instant feedback upon selecting an option."""
    app = ExamApp(questions=sample_questions, mode="study_drill")
    async with app.run_test() as pilot:
        # Initially explanation is hidden
        assert not app.is_explanation_visible

        # Select option 'b' (correct answer for Q0)
        await pilot.press("b")

        # Explanation should now be visible
        assert app.is_explanation_visible
        explanation_widget = app.query_one("#explanation-text")
        assert "doctoral degree" in str(explanation_widget.renderable)

        citation_widget = app.query_one("#explanation-citation")
        assert "O.C.G.A. § 43-39-8" in str(citation_widget.renderable)

        badge_widget = app.query_one("#explanation-badge")
        assert "CORRECT" in str(badge_widget.renderable).upper()


@pytest.mark.asyncio
async def test_confirmation_on_unanswered_submit(tmp_path: Path, sample_questions: list[dict]):
    """Test submit confirmation prompt when questions remain unanswered."""
    db_file = tmp_path / "test_gamb.db"
    init_db(db_file)
    app = ExamApp(questions=sample_questions, mode="timed_exam", db_path=db_file)
    async with app.run_test() as pilot:
        # Only answer question 0
        await pilot.press("b")

        # First press 's' triggers confirmation warning because 4 questions are unanswered
        await pilot.press("s")
        assert app.is_completed is False
        assert app.confirming_submit is True

        # Second press 's' confirms submission
        await pilot.press("s")
        assert app.is_completed is True
        assert app.score_data["total_correct"] == 1
        assert app.score_data["percentage"] == 20.0
        assert app.score_data["passed"] is False


@pytest.mark.asyncio
async def test_submit_cancellation_via_escape(tmp_path: Path, sample_questions: list[dict]):
    """Test cancelling submit confirmation prompt with Escape key."""
    db_file = tmp_path / "test_gamb.db"
    init_db(db_file)
    app = ExamApp(questions=sample_questions, mode="timed_exam", db_path=db_file)
    async with app.run_test() as pilot:
        # Answer question 0
        await pilot.press("b")

        # Press 's' triggers confirmation warning
        await pilot.press("s")
        assert app.confirming_submit is True
        assert app.is_completed is False

        # Press 'escape' cancels confirmation cleanly
        await pilot.press("escape")
        assert app.confirming_submit is False
        assert app.is_completed is False

        # Verify options are not overwritten during confirmation
        await pilot.press("s")
        assert app.confirming_submit is True
        # Pressing an option key when confirming should be blocked by guard
        await pilot.press("a")
        assert app.answers[0] == "B"  # Preserved original answer


@pytest.mark.asyncio
async def test_jump_to_question(sample_questions: list[dict]):
    """Test jumping directly to a specific question via jump grid."""
    app = ExamApp(questions=sample_questions, mode="timed_exam")
    async with app.run_test() as pilot:
        assert app.current_index == 0
        await pilot.press("j")
        assert app.jump_grid_open

        # Jump directly to question index 3 (Question 4)
        app.jump_to_question(3)
        assert app.current_index == 3
        assert not app.jump_grid_open

        # Reopen jump grid and click button for Q2 (index 1)
        await pilot.press("j")
        assert app.jump_grid_open
        await pilot.click("#jump-btn-1")
        assert app.current_index == 1
        assert not app.jump_grid_open


@pytest.mark.asyncio
async def test_numeric_key_selection(sample_questions: list[dict]):
    """Test selecting options using number keys 1, 2, 3, 4."""
    app = ExamApp(questions=sample_questions, mode="timed_exam")
    async with app.run_test() as pilot:
        await pilot.press("1")
        assert app.answers[0] == "A"
        await pilot.press("2")
        assert app.answers[0] == "B"
        await pilot.press("3")
        assert app.answers[0] == "C"
        await pilot.press("4")
        assert app.answers[0] == "D"


def test_score_cutoff_calculation():
    """Test passing vs failing cutoff rules (76% / 38 cutoff)."""
    # 50 questions: 38 is passing (76.0%)
    qs_50 = [
        {
            "id": i,
            "domain": "licensure",
            "question_text": f"Q{i}",
            "option_a": "A",
            "option_b": "B",
            "option_c": "C",
            "option_d": "D",
            "correct_option": "A",
            "explanation": "Exp",
            "source_citation": "Cite",
        }
        for i in range(50)
    ]

    app = ExamApp(questions=qs_50)
    # 38 correct answers
    for i in range(38):
        app.answers[i] = "A"
    score_data = app.calculate_score()
    assert score_data["total_correct"] == 38
    assert score_data["percentage"] == 76.0
    assert score_data["passed"] is True

    # 37 correct answers (74.0%) -> Fail
    app.answers.clear()
    for i in range(37):
        app.answers[i] = "A"
    score_data = app.calculate_score()
    assert score_data["total_correct"] == 37
    assert score_data["percentage"] == 74.0
    assert score_data["passed"] is False


@pytest.mark.asyncio
async def test_review_mode_after_submission(tmp_path: Path, sample_questions: list[dict]):
    """Test entering review mode after submitting the exam and returning via 'b'."""
    db_file = tmp_path / "test_gamb.db"
    init_db(db_file)
    app = ExamApp(questions=sample_questions, mode="timed_exam", db_path=db_file)
    async with app.run_test() as pilot:
        # Answer Q0 correctly ("B"), leave rest unanswered
        await pilot.press("b")
        await pilot.press("s")
        await pilot.press("s")  # confirm submit
        assert app.is_completed is True

        # Results screen should have navigation buttons hidden
        assert app.query_one("#btn-prev").display is False
        assert app.query_one("#btn-next").display is False

        # Press 'm' to review missed questions
        await pilot.press("m")
        assert app.review_mode is True
        assert app.review_filter == "missed"

        # Press 'b' in review mode returns to results screen
        await pilot.press("b")
        assert app.review_mode is False
        assert app.query_one("#results-container").display is True

        # Press 'r' to review all questions
        await pilot.press("r")
        assert app.review_mode is True
        assert app.review_filter == "all"

        # Press 'escape' in review mode also returns to results screen
        await pilot.press("escape")
        assert app.review_mode is False


@pytest.mark.asyncio
async def test_timer_expiration_auto_submit(tmp_path: Path, sample_questions: list[dict]):
    """Test auto-submission when countdown timer reaches zero."""
    db_file = tmp_path / "test_gamb.db"
    init_db(db_file)
    app = ExamApp(questions=sample_questions, mode="timed_exam", time_limit_seconds=2, db_path=db_file)
    async with app.run_test():
        assert app.is_completed is False
        app.time_remaining = 1
        app.timer_tick()
        assert app.time_remaining == 0
        assert app.is_completed is True
        assert app.score_data is not None


@pytest.mark.asyncio
async def test_option_choices_left_justified_and_preserved(sample_questions: list[dict]):
    """Test that multiple choice buttons are left-justified and markup tags are preserved."""
    app = ExamApp(questions=sample_questions, mode="timed_exam")
    async with app.run_test(size=(80, 24)) as pilot:
        for letter in ("a", "b", "c", "d"):
            btn = app.query_one(f"#option-{letter}")
            assert btn.styles.text_align == "left"
            assert btn.styles.content_align == ("left", "top")
            assert btn.styles.text_wrap == "wrap"

        btn_a = app.query_one("#option-a")
        btn_b = app.query_one("#option-b")
        # Verify bracket markers [ ] and [A], [B] are intact and not stripped as markup
        assert "[ ] [A] Master's degree" in btn_a.label.plain
        assert "[ ] [B] Doctoral degree" in btn_b.label.plain

        # Select option B
        await pilot.press("b")
        assert "[x] [B] Doctoral degree" in btn_b.label.plain
        assert "[ ] [A] Master's degree" in btn_a.label.plain


@pytest.mark.asyncio
async def test_option_choices_wrap_long_text_without_truncation():
    """Test that answer choices longer than terminal width wrap cleanly across lines without truncation."""
    long_opt_text = (
        "A comprehensive statutory requirement requiring candidate verification, "
        "supervised clinical hours under Board approved supervisor, and complete documentation "
        "retained for the prescribed legal period without truncation or clipping."
    )
    long_questions = [
        {
            "id": 1,
            "domain": "licensure",
            "subtopic": "Qualifications",
            "source_citation": "O.C.G.A. § 43-39-8",
            "question_text": "What is the detailed statutory requirement?",
            "option_a": long_opt_text,
            "option_b": "Short choice B",
            "option_c": "Short choice C",
            "option_d": "Short choice D",
            "correct_option": "A",
            "explanation": "Detailed explanation.",
        }
    ]

    # Test standard terminal width (80 columns)
    app = ExamApp(questions=long_questions, mode="study_drill")
    async with app.run_test(size=(80, 24)) as pilot:
        btn_a = app.query_one("#option-a")
        # Multi-line height due to wrapping
        assert btn_a.size.height >= 2
        rendered_text = " ".join(btn_a.render_line(y).text.strip() for y in range(btn_a.size.height))
        # Ensure start and end of string are intact
        assert "[ ] [A] A comprehensive" in rendered_text
        assert "without truncation or clipping." in rendered_text

        # Select A and verify it updates properly while wrapped
        await pilot.press("a")
        rendered_selected = " ".join(btn_a.render_line(y).text.strip() for y in range(btn_a.size.height))
        assert "[x] [A] A comprehensive" in rendered_selected

    # Test narrower terminal width (50 columns) - should wrap into even more lines
    app_narrow = ExamApp(questions=long_questions, mode="study_drill")
    async with app_narrow.run_test(size=(50, 24)):
        btn_a_narrow = app_narrow.query_one("#option-a")
        assert btn_a_narrow.size.height >= 4
        rendered_narrow = " ".join(btn_a_narrow.render_line(y).text.strip() for y in range(btn_a_narrow.size.height))
        assert "[ ] [A] A comprehensive" in rendered_narrow
        assert "without truncation or clipping." in rendered_narrow
