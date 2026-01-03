"""module."""

from pathlib import Path

from pyrig.dev.configs.testing.main_test import MainTestConfigFile


class TestMainTestConfigFile:
    """Test class."""

    def test_is_correct(self) -> None:
        """Test method."""
        assert MainTestConfigFile().is_correct()

    def test_get_parent_path(self) -> None:
        """Test method for get_parent_path."""
        assert isinstance(MainTestConfigFile.get_parent_path(), Path)

    def test_get_filename(self) -> None:
        """Test method for get_filename."""
        assert MainTestConfigFile.get_filename() == "test_main"

    def test_get_lines(self) -> None:
        """Test method for get_content_str."""
        lines = MainTestConfigFile.get_lines()
        content_str = "\n".join(lines)
        assert len(content_str) > 0
        assert "def test_main" in content_str
