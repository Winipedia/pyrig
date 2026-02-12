"""module."""

from pyrig.rig.tools.linter import Linter


class TestLinter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = Linter.L.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = Linter.L.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        result = Linter.L.name()
        assert result == "ruff"

    def test_check_args(self) -> None:
        """Test method."""
        result = Linter.L.check_args()
        assert result == ("ruff", "check")

    def test_check_fix_args(self) -> None:
        """Test method."""
        result = Linter.L.check_fix_args()
        assert result == ("ruff", "check", "--fix")

    def test_format_args(self) -> None:
        """Test method."""
        result = Linter.L.format_args()
        assert result == ("ruff", "format")
