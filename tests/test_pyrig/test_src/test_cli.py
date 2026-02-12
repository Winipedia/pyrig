"""module."""

from pyrig.src.cli import pkg_name_from_argv, project_name_from_argv


def test_project_name_from_argv() -> None:
    """Test function."""
    result = project_name_from_argv()
    assert isinstance(result, str), "Expected string result"


def test_pkg_name_from_argv() -> None:
    """Test function."""
    result = pkg_name_from_argv()
    assert isinstance(result, str), "Expected string result"
