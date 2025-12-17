"""module."""

from pyrig.dev.utils.cli import get_pkg_name_from_argv, get_project_name_from_argv


def test_get_project_name_from_argv() -> None:
    """Test function."""
    result = get_project_name_from_argv()
    assert isinstance(result, str), "Expected string result"


def test_get_pkg_name_from_argv() -> None:
    """Test function."""
    result = get_pkg_name_from_argv()
    assert isinstance(result, str), "Expected string result"
