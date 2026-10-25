"""Shared fixtures and configuration for pytest."""

from pathlib import Path
import pytest


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    """Return a path to a temporary database file."""
    return tmp_path / "test_gamb_exam.db"
