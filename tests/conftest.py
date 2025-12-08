"""Pytest configuration and shared fixtures."""

from pathlib import Path

import pytest  # type: ignore[import-not-found]


@pytest.fixture
def repo_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def python_tools_dir(repo_root: Path) -> Path:
    """Return the python tools directory."""
    return repo_root / "python"


@pytest.fixture
def bash_tools_dir(repo_root: Path) -> Path:
    """Return the bash tools directory."""
    return repo_root / "bash"
