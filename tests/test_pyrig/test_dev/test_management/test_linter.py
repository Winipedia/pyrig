"""module."""

from pyrig.dev.management.linter import Linter


class TestLinter:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = Linter.name()
        assert result == "ruff"

    def test_get_check_args(self) -> None:
        """Test method."""
        result = Linter.get_check_args()
        assert result == ("ruff", "check")

    def test_get_check_fix_args(self) -> None:
        """Test method."""
        result = Linter.get_check_fix_args()
        assert result == ("ruff", "check", "--fix")

    def test_get_format_args(self) -> None:
        """Test method."""
        result = Linter.get_format_args()
        assert result == ("ruff", "format")
