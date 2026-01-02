"""module."""

from pyrig.src.management.mdlinter import MDLinter


class TestMDLinter:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = MDLinter.name()
        assert result == "rumdl"

    def test_get_check_args(self) -> None:
        """Test method."""
        result = MDLinter.get_check_args()
        assert result == ("rumdl", "check")

    def test_get_check_fix_args(self) -> None:
        """Test method."""
        result = MDLinter.get_check_fix_args()
        assert result == ("rumdl", "check", "--fix")
