"""module."""

from pathlib import Path

from pyrig.rig.configs.docs.api import APIDocsConfigFile


class TestAPIDocsConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        assert APIDocsConfigFile.I.stem() == "api"

    def test_parent_path(self) -> None:
        """Test method."""
        assert APIDocsConfigFile.I.parent_path() == Path("docs")

    def test_lines(self) -> None:
        """Test method."""
        lines = APIDocsConfigFile.I.lines()
        content_str = "\n".join(lines)
        assert ":::" in content_str
