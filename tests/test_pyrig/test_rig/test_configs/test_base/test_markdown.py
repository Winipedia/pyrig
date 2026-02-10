"""module."""

from pyrig.rig.configs.base.markdown import MarkdownConfigFile


class TestMarkdownConfigFile:
    """Test class."""

    def test_get_file_extension(self) -> None:
        """Test method for get_file_extension."""
        expected = "md"
        actual = MarkdownConfigFile.get_file_extension()
        assert actual == expected, f"Expected {expected}, got {actual}"
