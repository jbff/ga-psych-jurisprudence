"""Terminal User Interface (TUI) Simulator for the Georgia Jurisprudence Exam.

Built with Textual and Rich, providing full-screen interactive exam simulation,
instant feedback study drills, flagged item tracking, jump navigation,
score calculation against official 76% (38/50) cutoffs, and SQLite persistence.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.css.query import NoMatches
from textual.timer import Timer
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Label,
    Static,
)

from gamb_exam.db import (
    complete_session,
    create_session,
    save_session_answer,
)
from gamb_exam.generator import (
    DOMAIN_DISPLAY_NAMES,
    PASSING_PERCENT,
    PASSING_SCORE,
)

logger = logging.getLogger(__name__)


class ContentStatic(Static):
    """Static text widget providing backward-compatible renderable access."""

    @property
    def renderable(self) -> Any:
        return self.content


class ExamApp(App[None]):
    """Textual Terminal User Interface for the Georgia Jurisprudence Practice Exam."""

    TITLE = "Georgia Psychology Jurisprudence Examination Simulator"
    SUB_TITLE = "Independent Study Engine & Diagnostic Reporter"

    CSS = """
    Screen {
        background: $surface;
        color: $text;
    }

    #header-bar {
        dock: top;
        height: 3;
        background: $panel;
        border-bottom: solid $accent;
        padding: 0 1;
        layout: horizontal;
        align: center middle;
    }

    #header-title {
        width: 35%;
        text-style: bold;
        color: $accent;
    }

    #header-timer {
        width: 20%;
        text-align: center;
        text-style: bold;
        color: $warning;
    }

    #header-tracker {
        width: 30%;
        text-align: center;
        text-style: bold;
    }

    #header-flag {
        width: 15%;
        text-align: right;
        color: $error;
        text-style: bold;
    }

    #main-container {
        height: 1fr;
        padding: 0 1;
    }

    #exam-container {
        height: 1fr;
        padding: 1;
    }

    #meta-container {
        height: auto;
        margin-bottom: 1;
    }

    .meta-badge {
        padding: 0 1;
        margin-right: 1;
        border: round $primary;
        text-style: bold;
    }

    #meta-subtopic {
        border: round $secondary;
        color: $secondary;
    }

    #question-text {
        margin: 1 0;
        padding: 1;
        border-left: thick $accent;
        background: $surface-lighten-1;
        text-style: bold;
    }

    #options-container {
        margin: 1 0;
        height: auto;
    }

    .option-btn {
        width: 100%;
        margin-bottom: 1;
        text-align: left;
    }

    #explanation-panel {
        margin: 1 0;
        padding: 1;
        border: solid $accent;
        background: $surface-lighten-2;
        height: auto;
    }

    #explanation-badge {
        text-style: bold;
        margin-bottom: 1;
    }

    #explanation-citation {
        text-style: italic;
        color: $accent;
        margin-bottom: 1;
    }

    #explanation-text {
        margin-bottom: 1;
    }

    #confirm-panel {
        padding: 1;
        margin: 1 0;
        border: heavy $warning;
        background: $warning-darken-3;
        color: $text;
        text-style: bold;
        text-align: center;
        height: auto;
    }

    #jump-grid-container {
        height: 1fr;
        padding: 1 2;
    }

    #jump-grid-title {
        text-style: bold;
        margin-bottom: 1;
    }

    #jump-grid-scroll {
        height: 1fr;
        layout: grid;
        grid-size: 5;
        grid-gutter: 1;
    }

    .jump-btn {
        height: 3;
        width: 100%;
    }

    #jump-grid-actions {
        height: 3;
        margin-top: 1;
        align: center middle;
    }

    #results-container {
        height: 1fr;
        padding: 1 2;
    }

    .banner-pass {
        background: green;
        color: white;
        text-style: bold;
        text-align: center;
        padding: 1;
        margin-bottom: 1;
    }

    .banner-fail {
        background: red;
        color: white;
        text-style: bold;
        text-align: center;
        padding: 1;
        margin-bottom: 1;
    }

    #results-summary {
        text-align: center;
        margin-bottom: 1;
    }

    #results-table {
        height: 12;
        margin: 1 0;
    }

    #results-actions {
        margin-top: 1;
        height: 3;
        layout: horizontal;
        align: center middle;
    }

    #results-actions Button {
        margin: 0 1;
    }

    #nav-bar {
        dock: bottom;
        height: 3;
        background: $panel;
        border-top: solid $primary;
        layout: horizontal;
        align: center middle;
        padding: 0 1;
    }

    #nav-bar Button {
        margin: 0 1;
    }
    """

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("a", "select_option('A')", "Select A", show=False),
        Binding("1", "select_option('A')", "Select A", show=False),
        Binding("b", "select_option('B')", "Select B", show=False),
        Binding("2", "select_option('B')", "Select B", show=False),
        Binding("c", "select_option('C')", "Select C", show=False),
        Binding("3", "select_option('C')", "Select C", show=False),
        Binding("d", "select_option('D')", "Select D", show=False),
        Binding("4", "select_option('D')", "Select D", show=False),
        Binding("n", "next_question", "Next"),
        Binding("right", "next_question", "Next", show=False),
        Binding("enter", "next_question", "Next", show=False),
        Binding("p", "prev_question", "Prev"),
        Binding("left", "prev_question", "Prev", show=False),
        Binding("f", "toggle_flag", "Flag"),
        Binding("j", "toggle_jump", "Jump Grid"),
        Binding("s", "submit_exam", "Submit"),
        Binding("r", "review_all", "Review All"),
        Binding("m", "review_missed", "Review Missed"),
        Binding("escape", "cancel_action", "Cancel", show=False),
        Binding("q", "quit_exam", "Quit"),
    ]

    def __init__(
        self,
        questions: list[dict[str, Any]],
        mode: str = "timed_exam",
        time_limit_seconds: int = 3600,
        db_path: Path | str | None = None,
        auto_save: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.questions: list[dict[str, Any]] = questions or []
        self.mode: str = mode
        self.time_limit_seconds: int = time_limit_seconds
        self.time_remaining: int = time_limit_seconds if mode == "timed_exam" else 0
        self.db_path: Path | str | None = db_path
        self.auto_save: bool = auto_save

        self.current_index: int = 0
        self.answers: dict[int, str] = {}
        self.flags: set[int] = set()
        self.question_times: dict[int, float] = {}
        self.session_start_time: float = time.monotonic()
        self.question_entered_at: float = time.monotonic()

        self.session_id: int | None = None
        self.is_completed: bool = False
        self.confirming_submit: bool = False
        self.jump_grid_open: bool = False

        self.review_mode: bool = False
        self.review_filter: str = "all"
        self.review_indices: list[int] = []
        self.score_data: dict[str, Any] | None = None
        self._timer: Timer | None = None

    @property
    def is_explanation_visible(self) -> bool:
        """Return True when answer feedback and statutory citations should be exposed."""
        return self.review_mode or (self.mode == "study_drill" and self.current_index in self.answers)

    def compose(self) -> ComposeResult:
        with Horizontal(id="header-bar"):
            yield Label("Georgia Jurisprudence Simulator", id="header-title")
            yield Label("", id="header-timer")
            yield Label("", id="header-tracker")
            yield Label("", id="header-flag")

        with Container(id="main-container"):
            # Question view
            with ScrollableContainer(id="exam-container"):
                with Horizontal(id="meta-container"):
                    yield Label("", id="meta-domain", classes="meta-badge")
                    yield Label("", id="meta-citation", classes="meta-badge")
                    yield Label("", id="meta-subtopic", classes="meta-badge")

                yield ContentStatic("", id="question-text")

                with Vertical(id="options-container"):
                    yield Button("", id="option-a", classes="option-btn")
                    yield Button("", id="option-b", classes="option-btn")
                    yield Button("", id="option-c", classes="option-btn")
                    yield Button("", id="option-d", classes="option-btn")

                with Vertical(id="explanation-panel"):
                    yield ContentStatic("", id="explanation-badge")
                    yield ContentStatic("", id="explanation-citation")
                    yield ContentStatic("", id="explanation-text")

                with Vertical(id="confirm-panel"):
                    yield Label("", id="confirm-text")

            # Jump grid view
            with Vertical(id="jump-grid-container"):
                yield Label("Select a question to jump to:", id="jump-grid-title")
                with ScrollableContainer(id="jump-grid-scroll"):
                    for idx in range(len(self.questions)):
                        yield Button(f"Q{idx + 1}", id=f"jump-btn-{idx}", classes="jump-btn")
                with Horizontal(id="jump-grid-actions"):
                    yield Button("Close Jump Grid [J]", id="btn-close-jump")

            # Results view
            with ScrollableContainer(id="results-container"):
                yield ContentStatic("", id="results-banner")
                yield ContentStatic("", id="results-summary")
                yield DataTable(id="results-table")
                with Horizontal(id="results-actions"):
                    yield Button("[R] Review All", id="btn-review-all", variant="primary")
                    yield Button("[M] Review Missed", id="btn-review-missed", variant="warning")
                    yield Button("[Q] Quit", id="btn-quit", variant="error")

        with Horizontal(id="nav-bar"):
            yield Button("[P] Prev", id="btn-prev")
            yield Button("[N] Next", id="btn-next")
            yield Button("[F] Flag", id="btn-flag")
            yield Button("[J] Jump Grid", id="btn-jump")
            yield Button("[S] Submit", id="btn-submit", variant="success")
            yield Button("[B] Back to Results", id="btn-back-results", variant="primary")
            yield Button("[Q] Quit", id="btn-nav-quit")

        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Domain", "Correct", "Total", "Percentage", "Status")

        self.session_start_time = time.monotonic()
        self.question_entered_at = time.monotonic()
        self._timer = self.set_interval(1.0, self.timer_tick)

        self.update_header()
        self.update_layout_visibility()
        self.update_question_view()

    def _record_question_time(self) -> None:
        """Accurately accumulate wall-clock time spent on the active question."""
        if self.is_completed:
            return
        now = time.monotonic()
        if self.question_entered_at is not None:
            elapsed = now - self.question_entered_at
            if elapsed > 0:
                self.question_times[self.current_index] = (
                    self.question_times.get(self.current_index, 0.0) + elapsed
                )
        self.question_entered_at = now

    def timer_tick(self) -> None:
        if self.is_completed:
            return
        if not self.jump_grid_open:
            self._record_question_time()
        if self.mode == "timed_exam" and self.time_remaining > 0:
            self.time_remaining -= 1
            self.update_header()
            if self.time_remaining <= 0:
                self.submit_exam(force=True)

    def update_header(self) -> None:
        try:
            timer_widget = self.query_one("#header-timer", Label)
            tracker_widget = self.query_one("#header-tracker", Label)
            flag_widget = self.query_one("#header-flag", Label)
        except NoMatches:
            return

        if self.mode == "timed_exam":
            mins = self.time_remaining // 60
            secs = self.time_remaining % 60
            timer_widget.update(f"⏱ {mins:02d}:{secs:02d}")
        else:
            timer_widget.update("⏱ Study Mode")

        total_q = len(self.questions)
        if self.review_mode:
            rev_total = len(self.review_indices)
            rev_pos = (
                self.review_indices.index(self.current_index) + 1
                if self.current_index in self.review_indices
                else 1
            )
            tracker_widget.update(f"Review: {rev_pos} of {rev_total} (Q{self.current_index + 1})")
        else:
            tracker_widget.update(f"Question {self.current_index + 1} of {total_q}")

        if self.current_index in self.flags:
            flag_widget.update("🚩 FLAGGED")
        else:
            flag_widget.update("")

    def update_layout_visibility(self) -> None:
        try:
            exam_c = self.query_one("#exam-container")
            jump_c = self.query_one("#jump-grid-container")
            results_c = self.query_one("#results-container")
            btn_prev = self.query_one("#btn-prev")
            btn_next = self.query_one("#btn-next")
            btn_flag = self.query_one("#btn-flag")
            btn_jump = self.query_one("#btn-jump")
            btn_submit = self.query_one("#btn-submit")
            btn_back_results = self.query_one("#btn-back-results")
        except NoMatches:
            return

        if self.jump_grid_open:
            exam_c.display = False
            jump_c.display = True
            results_c.display = False
            btn_prev.display = False
            btn_next.display = False
            btn_flag.display = False
            btn_jump.display = True
            btn_submit.display = False
            btn_back_results.display = False
        elif self.is_completed and not self.review_mode:
            exam_c.display = False
            jump_c.display = False
            results_c.display = True
            btn_prev.display = False
            btn_next.display = False
            btn_flag.display = False
            btn_jump.display = False
            btn_submit.display = False
            btn_back_results.display = False
        elif self.review_mode:
            exam_c.display = True
            jump_c.display = False
            results_c.display = False
            btn_prev.display = True
            btn_next.display = True
            btn_flag.display = False
            btn_jump.display = False
            btn_submit.display = False
            btn_back_results.display = True
        else:
            exam_c.display = True
            jump_c.display = False
            results_c.display = False
            btn_prev.display = True
            btn_next.display = True
            btn_flag.display = True
            btn_jump.display = True
            btn_submit.display = True
            btn_back_results.display = False

    def update_question_view(self) -> None:
        if not self.questions or self.current_index >= len(self.questions):
            return

        q = self.questions[self.current_index]

        dom = q.get("domain", "")
        dom_display = DOMAIN_DISPLAY_NAMES.get(dom, dom.replace("-", " ").title())
        self.query_one("#meta-domain", Label).update(f"Domain: {dom_display}")
        self.query_one("#meta-citation", Label).update(f"Citation: {q.get('source_citation', 'N/A')}")

        subtopic = q.get("subtopic")
        subtopic_widget = self.query_one("#meta-subtopic", Label)
        if subtopic:
            subtopic_widget.update(f"Subtopic: {subtopic}")
            subtopic_widget.display = True
        else:
            subtopic_widget.display = False

        self.query_one("#question-text", ContentStatic).update(
            f"{self.current_index + 1}. {q.get('question_text', '')}"
        )

        selected_opt = self.answers.get(self.current_index)
        correct_opt = q.get("correct_option", "").strip().upper()
        show_feedback = self.is_explanation_visible

        for letter in ("A", "B", "C", "D"):
            btn = self.query_one(f"#option-{letter.lower()}", Button)
            opt_text = q.get(f"option_{letter.lower()}", "")
            is_selected = selected_opt == letter
            marker = "[x]" if is_selected else "[ ]"
            btn.label = f"{marker} [{letter}] {opt_text}"

            if show_feedback:
                if letter == correct_opt:
                    btn.variant = "success"
                elif is_selected:
                    btn.variant = "error"
                else:
                    btn.variant = "default"
            else:
                if is_selected:
                    btn.variant = "primary"
                else:
                    btn.variant = "default"

        exp_panel = self.query_one("#explanation-panel")
        if show_feedback:
            exp_panel.display = True
            badge = self.query_one("#explanation-badge", ContentStatic)
            citation = self.query_one("#explanation-citation", ContentStatic)
            text = self.query_one("#explanation-text", ContentStatic)

            is_user_correct = selected_opt == correct_opt
            if is_user_correct:
                badge.update("✅ CORRECT")
            else:
                badge.update(f"❌ INCORRECT — Correct Answer: [{correct_opt}]")

            citation.update(f"Statutory Citation: {q.get('source_citation', 'N/A')}")
            text.update(f"Explanation:\n{q.get('explanation', '')}")
        else:
            exp_panel.display = False

        confirm_panel = self.query_one("#confirm-panel")
        if self.confirming_submit:
            confirm_panel.display = True
            unanswered = len(self.questions) - len(self.answers)
            self.query_one("#confirm-text", Label).update(
                f"⚠️ Warning: {unanswered} question(s) remain unanswered!\n"
                "Press [S] again to confirm submission, or [Esc] to cancel."
            )
        else:
            confirm_panel.display = False

        self.update_header()

    def update_jump_grid(self) -> None:
        for idx in range(len(self.questions)):
            try:
                btn = self.query_one(f"#jump-btn-{idx}", Button)
            except NoMatches:
                continue

            ans = self.answers.get(idx)
            is_flagged = idx in self.flags
            parts = [f"Q{idx + 1}"]
            if is_flagged:
                parts.append("🚩")
            if ans:
                parts.append(f"[{ans}]")
            btn.label = " ".join(parts)

            if idx == self.current_index:
                btn.variant = "primary"
            elif is_flagged:
                btn.variant = "warning"
            elif ans:
                btn.variant = "success"
            else:
                btn.variant = "default"

    def calculate_score(self) -> dict[str, Any]:
        total_questions = len(self.questions)
        total_correct = sum(
            1
            for idx, q in enumerate(self.questions)
            if self.answers.get(idx) == q.get("correct_option")
        )
        percentage = round((total_correct / total_questions) * 100.0, 1) if total_questions > 0 else 0.0
        passed = (total_correct >= PASSING_SCORE) if total_questions == 50 else (percentage >= PASSING_PERCENT)

        domain_stats: dict[str, dict[str, Any]] = {}
        for idx, q in enumerate(self.questions):
            dom = q.get("domain", "unknown")
            if dom not in domain_stats:
                domain_stats[dom] = {
                    "name": DOMAIN_DISPLAY_NAMES.get(dom, dom.replace("-", " ").title()),
                    "total": 0,
                    "correct": 0,
                }
            domain_stats[dom]["total"] += 1
            if self.answers.get(idx) == q.get("correct_option"):
                domain_stats[dom]["correct"] += 1

        for dom, stat in domain_stats.items():
            tot = stat["total"]
            corr = stat["correct"]
            pct = round((corr / tot) * 100.0, 1) if tot > 0 else 0.0
            stat["percentage"] = pct
            stat["mastery"] = pct >= PASSING_PERCENT

        return {
            "total_correct": total_correct,
            "total_questions": total_questions,
            "percentage": percentage,
            "passed": passed,
            "domain_stats": domain_stats,
        }

    def submit_exam(self, force: bool = False) -> None:
        """Submit the exam and calculate diagnostic results.

        Prompts confirmation if unanswered questions remain unless force=True.
        """
        if self.is_completed:
            return

        unanswered = [i for i in range(len(self.questions)) if i not in self.answers]
        if unanswered and not force and not self.confirming_submit:
            self.confirming_submit = True
            self.update_question_view()
            return

        self._record_question_time()
        self.score_data = self.calculate_score()
        self.is_completed = True
        self.confirming_submit = False
        self.jump_grid_open = False

        if self._timer is not None:
            self._timer.stop()

        if self.auto_save:
            self._persist_to_db()

        self.update_layout_visibility()
        self.update_results_view()

    def _persist_to_db(self) -> None:
        try:
            self._record_question_time()
            elapsed_session = round(time.monotonic() - self.session_start_time)
            total_q_time = round(sum(self.question_times.values()))
            if self.mode == "timed_exam":
                time_spent = max(
                    self.time_limit_seconds - self.time_remaining,
                    elapsed_session,
                    total_q_time,
                )
            else:
                time_spent = max(elapsed_session, total_q_time)

            if self.session_id is None:
                self.session_id = create_session(
                    mode=self.mode,
                    total_questions=len(self.questions),
                    db_path=self.db_path,
                )

            for idx, q in enumerate(self.questions):
                selected = self.answers.get(idx)
                is_correct = selected == q.get("correct_option")
                flagged = idx in self.flags
                raw_time = self.question_times.get(idx, 0.0)
                q_time = max(1, round(raw_time)) if raw_time > 0 else 0
                q_id = q.get("id")
                if q_id is not None:
                    save_session_answer(
                        session_id=self.session_id,
                        question_id=q_id,
                        selected_option=selected,
                        is_correct=is_correct,
                        flagged=flagged,
                        time_spent_seconds=q_time,
                        db_path=self.db_path,
                    )

            if self.score_data is not None:
                complete_session(
                    session_id=self.session_id,
                    score=self.score_data["total_correct"],
                    percentage=self.score_data["percentage"],
                    passed=self.score_data["passed"],
                    time_spent_seconds=time_spent,
                    db_path=self.db_path,
                )
        except Exception:
            logger.exception("Failed to persist exam session to database")

    def update_results_view(self) -> None:
        if self.score_data is None:
            self.score_data = self.calculate_score()

        banner = self.query_one("#results-banner", ContentStatic)
        summary = self.query_one("#results-summary", ContentStatic)
        table = self.query_one("#results-table", DataTable)

        total = self.score_data["total_questions"]
        correct = self.score_data["total_correct"]
        pct = self.score_data["percentage"]
        passed = self.score_data["passed"]

        if passed:
            banner.remove_class("banner-fail")
            banner.add_class("banner-pass")
            banner.update(
                f"🏆 PASS — SCORE: {correct}/{total} ({pct:.1f}%)\n"
                f"Passing Cutoff: >= {PASSING_PERCENT}% ({PASSING_SCORE}/50)"
            )
        else:
            banner.remove_class("banner-pass")
            banner.add_class("banner-fail")
            banner.update(
                f"❌ DID NOT PASS — SCORE: {correct}/{total} ({pct:.1f}%)\n"
                f"Passing Cutoff: >= {PASSING_PERCENT}% ({PASSING_SCORE}/50)"
            )

        summary.update(
            f"Mode: {self.mode.replace('_', ' ').title()}  •  "
            f"Correct: {correct}  •  Missed: {total - correct}  •  "
            f"Total Questions: {total}"
        )

        table.clear()
        for stats in self.score_data["domain_stats"].values():
            status_text = "Mastery (>=76%)" if stats["mastery"] else "Needs Review (<76%)"
            table.add_row(
                stats["name"],
                str(stats["correct"]),
                str(stats["total"]),
                f"{stats['percentage']:.1f}%",
                status_text,
            )

    # Actions
    def action_select_option(self, option: str) -> None:
        if self.confirming_submit or self.jump_grid_open:
            return
        if self.is_completed and not self.review_mode:
            return
        if self.review_mode:
            if option.upper() == "B":
                self.action_back_to_results()
            return
        self.answers[self.current_index] = option.upper()
        self.update_question_view()

    def action_next_question(self) -> None:
        if self.jump_grid_open or (self.is_completed and not self.review_mode):
            return
        self.confirming_submit = False
        if not self.review_mode and not self.is_completed:
            self._record_question_time()
        if self.review_mode:
            if self.review_indices:
                try:
                    pos = self.review_indices.index(self.current_index)
                    if pos < len(self.review_indices) - 1:
                        self.current_index = self.review_indices[pos + 1]
                except ValueError:
                    self.current_index = self.review_indices[0]
        else:
            if self.current_index < len(self.questions) - 1:
                self.current_index += 1
        self.update_question_view()

    def action_prev_question(self) -> None:
        if self.jump_grid_open or (self.is_completed and not self.review_mode):
            return
        self.confirming_submit = False
        if not self.review_mode and not self.is_completed:
            self._record_question_time()
        if self.review_mode:
            if self.review_indices:
                try:
                    pos = self.review_indices.index(self.current_index)
                    if pos > 0:
                        self.current_index = self.review_indices[pos - 1]
                except ValueError:
                    self.current_index = self.review_indices[0]
        else:
            if self.current_index > 0:
                self.current_index -= 1
        self.update_question_view()

    def action_toggle_flag(self) -> None:
        if self.jump_grid_open or (self.is_completed and not self.review_mode):
            return
        self.confirming_submit = False
        if self.current_index in self.flags:
            self.flags.remove(self.current_index)
        else:
            self.flags.add(self.current_index)
        self.update_header()

    def action_toggle_jump(self) -> None:
        if self.is_completed and not self.review_mode:
            return
        self.confirming_submit = False
        if not self.review_mode and not self.is_completed:
            if not self.jump_grid_open:
                self._record_question_time()
            else:
                self.question_entered_at = time.monotonic()
        self.jump_grid_open = not self.jump_grid_open
        self.update_layout_visibility()
        if self.jump_grid_open:
            self.update_jump_grid()
        else:
            self.update_question_view()

    def jump_to_question(self, index: int) -> None:
        if 0 <= index < len(self.questions):
            if not self.review_mode and not self.is_completed and not self.jump_grid_open:
                self._record_question_time()
            self.current_index = index
            self.question_entered_at = time.monotonic()
            self.jump_grid_open = False
            self.confirming_submit = False
            self.update_layout_visibility()
            self.update_question_view()

    def action_submit_exam(self) -> None:
        if self.is_completed:
            return
        unanswered = [i for i in range(len(self.questions)) if i not in self.answers]
        if unanswered and not self.confirming_submit:
            self.confirming_submit = True
            self.update_question_view()
            return
        self.submit_exam(force=True)

    def action_review_all(self) -> None:
        if not self.is_completed:
            return
        self.review_mode = True
        self.review_filter = "all"
        self.review_indices = list(range(len(self.questions)))
        self.current_index = self.review_indices[0] if self.review_indices else 0
        self.update_layout_visibility()
        self.update_question_view()

    def action_review_missed(self) -> None:
        if not self.is_completed:
            return
        self.review_mode = True
        self.review_filter = "missed"
        missed = [
            i
            for i, q in enumerate(self.questions)
            if self.answers.get(i) != q.get("correct_option")
        ]
        self.review_indices = missed if missed else list(range(len(self.questions)))
        self.current_index = self.review_indices[0] if self.review_indices else 0
        self.update_layout_visibility()
        self.update_question_view()

    def action_back_to_results(self) -> None:
        if not self.is_completed:
            return
        self.review_mode = False
        self.update_layout_visibility()
        self.update_results_view()

    def action_cancel_action(self) -> None:
        if self.confirming_submit:
            self.confirming_submit = False
            self.update_question_view()
        elif self.jump_grid_open:
            self.jump_grid_open = False
            self.update_layout_visibility()
            self.update_question_view()
        elif self.review_mode:
            self.action_back_to_results()

    def action_quit_exam(self) -> None:
        self.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "option-a":
            self.action_select_option("A")
        elif btn_id == "option-b":
            self.action_select_option("B")
        elif btn_id == "option-c":
            self.action_select_option("C")
        elif btn_id == "option-d":
            self.action_select_option("D")
        elif btn_id == "btn-prev":
            self.action_prev_question()
        elif btn_id == "btn-next":
            self.action_next_question()
        elif btn_id == "btn-flag":
            self.action_toggle_flag()
        elif btn_id in ("btn-jump", "btn-close-jump"):
            self.action_toggle_jump()
        elif btn_id == "btn-submit":
            self.action_submit_exam()
        elif btn_id == "btn-review-all":
            self.action_review_all()
        elif btn_id == "btn-review-missed":
            self.action_review_missed()
        elif btn_id == "btn-back-results":
            self.action_back_to_results()
        elif btn_id in ("btn-quit", "btn-nav-quit"):
            self.action_quit_exam()
        elif btn_id.startswith("jump-btn-"):
            idx = int(btn_id.replace("jump-btn-", ""))
            self.jump_to_question(idx)
