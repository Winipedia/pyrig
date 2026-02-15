"""module."""

from pathlib import Path

from pyrig.rig.configs.markdown.docs.api import ApiConfigFile


class TestApiConfigFile:
    """Test class."""

    def test_parent_path(self) -> None:
        """Test method."""
        assert ApiConfigFile.I.parent_path() == Path("docs")

    def test_lines(self) -> None:
        """Test method."""
        lines = ApiConfigFile.I.lines()
        content_str = "\n".join(lines)
        assert ":::" in content_str
