"""module."""

from pathlib import Path

from pyrig.dev.configs.markdown.docs.api import ApiConfigFile


class TestApiConfigFile:
    """Test class."""

    def test_get_parent_path(self) -> None:
        """Test method."""
        assert ApiConfigFile.get_parent_path() == Path("docs")

    def test_get_lines(self) -> None:
        """Test method."""
        lines = ApiConfigFile.get_lines()
        content_str = "\n".join(lines)
        assert ":::" in content_str
