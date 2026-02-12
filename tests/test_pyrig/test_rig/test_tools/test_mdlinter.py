"""module."""

from pyrig.rig.tools.mdlinter import MDLinter


class TestMDLinter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = MDLinter.L.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = MDLinter.L.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        result = MDLinter.L.name()
        assert result == "rumdl"

    def test_get_check_args(self) -> None:
        """Test method."""
        result = MDLinter.L.get_check_args()
        assert result == ("rumdl", "check")

    def test_get_check_fix_args(self) -> None:
        """Test method."""
        result = MDLinter.L.get_check_fix_args()
        assert result == ("rumdl", "check", "--fix")
