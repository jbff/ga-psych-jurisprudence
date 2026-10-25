"""Command-line interface and entry points for the Georgia Jurisprudence Exam Suite."""

from __future__ import annotations

import argparse
import random
import sqlite3
import sys
from collections.abc import Sequence
from pathlib import Path

from rich.console import Console
from rich.table import Table

from gamb_exam.db import (
    DEFAULT_DB_PATH,
    get_all_questions,
    get_missed_questions,
    get_questions_by_domain,
    get_session_history,
    init_db,
)
from gamb_exam.generator import (
    export_mock_markdown,
    generate_exam_questions,
    shuffle_question_options,
)

console = Console()


def handle_test(args: argparse.Namespace) -> int:
    """Handle the 'test' subcommand to run a timed 50-question simulation."""
    rng = random.Random(args.seed) if args.seed is not None else None
    try:
        questions = generate_exam_questions(
            db_path=args.db,
            prioritize_unseen=not args.no_unseen,
            rng=rng,
        )
    except (ValueError, sqlite3.Error) as err:
        console.print(
            f"[bold red]Error generating practice exam:[/bold red] {err}\n"
            "[yellow]Database may be missing or unseeded. Run question seeding first![/yellow]"
        )
        return 1

    from gamb_exam.tui import ExamApp

    app = ExamApp(questions=questions, mode="timed_exam", db_path=args.db)
    app.run()
    return 0


def handle_study(args: argparse.Namespace) -> int:
    """Handle the 'study' subcommand to run an untimed drill with instant feedback."""
    if args.domain:
        questions = get_questions_by_domain(
            args.domain, db_path=args.db, limit=None
        )
        random.shuffle(questions)
        if args.count and len(questions) > args.count:
            questions = questions[: args.count]
    else:
        questions = get_all_questions(db_path=args.db)
        random.shuffle(questions)
        if args.count and len(questions) > args.count:
            questions = questions[: args.count]

    if not questions:
        console.print("[yellow]No questions found for study drill.[/yellow]")
        return 0

    questions = [shuffle_question_options(q) for q in questions]

    from gamb_exam.tui import ExamApp

    app = ExamApp(questions=questions, mode="study_drill", db_path=args.db)
    app.run()
    return 0


def handle_missed(args: argparse.Namespace) -> int:
    """Handle the 'missed' subcommand to drill previously failed questions."""
    missed = get_missed_questions(db_path=args.db)
    if not missed:
        console.print(
            "[yellow]No missed questions found in exam history. "
            "Take a practice exam first! [cyan](gamb-exam test)[/cyan][/yellow]"
        )
        return 0

    random.shuffle(missed)
    missed = [shuffle_question_options(q) for q in missed]

    from gamb_exam.tui import ExamApp

    app = ExamApp(questions=missed, mode="study_drill", db_path=args.db)
    app.run()
    return 0


def handle_stats(args: argparse.Namespace) -> int:
    """Handle the 'stats' subcommand to display past session results."""
    init_db(args.db)
    sessions = get_session_history(db_path=args.db, limit=args.limit)
    if not sessions:
        console.print(
            "[yellow]No exam history found. "
            "Complete a practice exam first! [cyan](gamb-exam test)[/cyan][/yellow]"
        )
        return 0

    table = Table(title="Georgia Jurisprudence Exam History")
    table.add_column("Session ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Date/Time", justify="center", no_wrap=True)
    table.add_column("Mode", justify="center")
    table.add_column("Score", justify="center", no_wrap=True)
    table.add_column("Percentage", justify="right", no_wrap=True)
    table.add_column("Status", justify="center", no_wrap=True)
    table.add_column("Time Spent", justify="right", no_wrap=True)

    for s in sessions:
        score_val = s.get("score")
        total_val = s.get("total_questions", 50)
        score_str = f"{score_val}/{total_val}" if score_val is not None else "N/A"

        pct_val = s.get("percentage")
        pct_str = f"{pct_val:.1f}%" if pct_val is not None else "N/A"

        passed = s.get("passed")
        if passed is True or passed == 1:
            status_str = "[bold green]PASS[/bold green]"
        elif passed is False or passed == 0:
            status_str = "[bold red]FAIL[/bold red]"
        else:
            status_str = "[dim]INCOMPLETE[/dim]"

        time_spent = s.get("time_spent_seconds")
        if time_spent is not None:
            m = time_spent // 60
            sec = time_spent % 60
            time_str = f"{m:02d}:{sec:02d}"
        else:
            time_str = "N/A"

        date_str = str(s.get("completed_at") or s.get("started_at") or "N/A")

        table.add_row(
            str(s["id"]),
            date_str,
            str(s.get("mode", "")),
            score_str,
            pct_str,
            status_str,
            time_str,
        )

    console.print(table)
    console.print()

    total_exams = len(sessions)
    completed_sessions = [s for s in sessions if s.get("passed") is not None]
    passing_exams = sum(1 for s in completed_sessions if s.get("passed") in (True, 1))
    pass_rate = (
        (passing_exams / len(completed_sessions) * 100.0) if completed_sessions else 0.0
    )
    pcts = [s["percentage"] for s in sessions if s.get("percentage") is not None]
    avg_score = (sum(pcts) / len(pcts)) if pcts else 0.0

    console.print(
        f"[bold]Total exams:[/bold] {total_exams} | "
        f"[bold]Passing exams:[/bold] {passing_exams} | "
        f"[bold]Pass rate:[/bold] {pass_rate:.1f}% | "
        f"[bold]Average score:[/bold] {avg_score:.1f}%"
    )
    return 0


def handle_export(args: argparse.Namespace) -> int:
    """Handle the 'export' subcommand to generate markdown mock exams and answer keys."""
    try:
        questions = generate_exam_questions(db_path=args.db)
        q_path, k_path = export_mock_markdown(
            questions,
            output_dir=args.output,
            mock_id=args.mock_id,
        )
    except (ValueError, sqlite3.Error) as err:
        console.print(
            f"[bold red]Error exporting mock exam:[/bold red] {err}\n"
            "[yellow]Database may be missing or unseeded. Run question seeding first![/yellow]"
        )
        return 1

    console.print("[bold green]Successfully exported mock exam:[/bold green]")
    console.print(f"  [bold]Questions:[/bold] [cyan]{q_path}[/cyan]", soft_wrap=True)
    console.print(f"  [bold]Answer Key:[/bold] [cyan]{k_path}[/cyan]", soft_wrap=True)
    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="gamb-exam",
        description="Georgia Psychology Jurisprudence Examination Simulator and Study Suite",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="gamb-exam 1.0.0",
        help="Show program's version number and exit",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # 1. test
    test_parser = subparsers.add_parser(
        "test",
        help="Start a timed 50-question jurisprudence exam simulation",
    )
    test_parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database file (default: {DEFAULT_DB_PATH})",
    )
    test_parser.add_argument(
        "--no-unseen",
        action="store_true",
        default=False,
        help="Disable unseen question prioritization",
    )
    test_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for deterministic question generation",
    )
    test_parser.set_defaults(func=handle_test)

    # 2. study
    study_parser = subparsers.add_parser(
        "study",
        help="Start an untimed study drill with immediate explanations",
    )
    study_parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database file (default: {DEFAULT_DB_PATH})",
    )
    study_parser.add_argument(
        "--domain",
        choices=[
            "prof-relationships",
            "licensure",
            "competence",
            "assessment",
            "privacy",
            "recordkeeping",
        ],
        default=None,
        help="Filter study drill questions to a specific jurisprudence domain",
    )
    study_parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="Number of questions to include in the study drill (default: 50)",
    )
    study_parser.set_defaults(func=handle_study)

    # 3. missed
    missed_parser = subparsers.add_parser(
        "missed",
        help="Practice previously missed questions in study drill mode",
    )
    missed_parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database file (default: {DEFAULT_DB_PATH})",
    )
    missed_parser.set_defaults(func=handle_missed)

    # 4. stats
    stats_parser = subparsers.add_parser(
        "stats",
        help="View past exam session statistics and performance history",
    )
    stats_parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database file (default: {DEFAULT_DB_PATH})",
    )
    stats_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of historical sessions to display (default: 20)",
    )
    stats_parser.set_defaults(func=handle_stats)

    # 5. export
    export_parser = subparsers.add_parser(
        "export",
        help="Export a 50-question mock exam and answer key to Markdown",
    )
    export_parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to SQLite database file (default: {DEFAULT_DB_PATH})",
    )
    export_parser.add_argument(
        "--output",
        type=Path,
        default=Path("mocks"),
        help="Directory where mock exam markdown files will be written (default: mocks/)",
    )
    export_parser.add_argument(
        "--mock-id",
        type=str,
        default=None,
        help="Optional identifier or number suffix for generated mock files",
    )
    export_parser.set_defaults(func=handle_export)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for the Georgia Jurisprudence Examination suite."""
    try:
        parser = create_parser()

        if argv is None:
            argv = sys.argv[1:]

        if not argv:
            parser.print_help()
            return 0

        try:
            args = parser.parse_args(argv)
        except SystemExit as exc:
            return exc.code if isinstance(exc.code, int) else 0

        if not hasattr(args, "func") or args.func is None:
            parser.print_help()
            return 0

        return args.func(args)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
