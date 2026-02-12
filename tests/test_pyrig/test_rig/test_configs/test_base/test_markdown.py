"""module."""

from pyrig.rig.configs.base.markdown import MarkdownConfigFile


class TestMarkdownConfigFile:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        expected = "md"
        actual = MarkdownConfigFile.extension()
        assert actual == expected, f"Expected {expected}, got {actual}"
