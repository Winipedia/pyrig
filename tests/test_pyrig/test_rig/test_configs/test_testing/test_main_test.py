"""module."""

from pathlib import Path

from pyrig.rig.configs.testing.main_test import MainTestConfigFile


class TestMainTestConfigFile:
    """Test class."""

    def test_is_correct(self) -> None:
        """Test method."""
        assert MainTestConfigFile.I.is_correct()

    def test_parent_path(self) -> None:
        """Test method."""
        assert isinstance(MainTestConfigFile.I.parent_path(), Path)

    def test_filename(self) -> None:
        """Test method."""
        assert MainTestConfigFile.I.filename() == "test_main"

    def test_lines(self) -> None:
        """Test method."""
        lines = MainTestConfigFile.I.lines()
        content_str = "\n".join(lines)
        assert len(content_str) > 0
        assert "def test_main" in content_str
