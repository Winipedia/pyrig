"""module."""

from pyrig.rig.tools.mdlinter import MDLinter


class TestMDLinter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = MDLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = MDLinter.I.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        result = MDLinter.I.name()
        assert result == "rumdl"

    def test_check_args(self) -> None:
        """Test method."""
        result = MDLinter.I.check_args()
        assert result == ("rumdl", "check")

    def test_check_fix_args(self) -> None:
        """Test method."""
        result = MDLinter.I.check_fix_args()
        assert result == ("rumdl", "check", "--fix")
