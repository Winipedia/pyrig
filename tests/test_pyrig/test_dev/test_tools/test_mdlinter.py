"""module."""

from pyrig.dev.tools.mdlinter import MDLinter


class TestMDLinter:
    """Test class."""

    def test_get_ignore_too_long_line_start(self) -> None:
        """Test method."""
        result = MDLinter.L.get_ignore_too_long_line_start()
        assert result == "<!-- rumdl-disable MD013 -->"

    def test_get_ignore_too_long_line_end(self) -> None:
        """Test method."""
        result = MDLinter.L.get_ignore_too_long_line_end()
        assert result == "<!-- rumdl-enable MD013 -->"

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
