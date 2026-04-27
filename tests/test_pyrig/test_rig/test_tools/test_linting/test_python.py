"""module."""

from pyrig.rig.tools.linting import python
from pyrig.rig.tools.linting.python import PythonLinter


class TestPythonLinter:
    """Test class."""

    def test_pydocstyle(self) -> None:
        """Test method."""
        assert PythonLinter.I.pydocstyle() == "google"

    def test_group(self) -> None:
        """Test method."""
        result = PythonLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = PythonLinter.I.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        result = PythonLinter.I.name()
        assert result == "ruff"

    def test_check_args(self) -> None:
        """Test method."""
        result = PythonLinter.I.check_args()
        assert result == ("ruff", "check")

    def test_check_fix_args(self) -> None:
        """Test method."""
        result = PythonLinter.I.check_fix_args()
        assert result == ("ruff", "check", "--fix")

    def test_format_args(self) -> None:
        """Test method."""
        result = PythonLinter.I.format_args()
        assert result == ("ruff", "format")


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        python.__doc__
        == """Wrapper around the PythonLinter tool.

Wraps PythonLinter commands and information.
"""
    )
