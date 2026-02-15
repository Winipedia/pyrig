"""module."""

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.configs.markdown.readme import ReadmeConfigFile


class TestMarkdownConfigFile:
    """Test class."""

    def test_extension(self) -> None:
        """Test method."""
        expected = "md"
        assert issubclass(ReadmeConfigFile, MarkdownConfigFile), (
            "ReadmeConfigFile should inherit from MarkdownConfigFile"
        )
        actual = ReadmeConfigFile().extension()
        assert actual == expected, f"Expected {expected}, got {actual}"
