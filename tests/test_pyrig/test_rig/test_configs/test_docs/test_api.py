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

    def test_content(self) -> None:
        """Test method."""
        content = APIDocsConfigFile.I.content()
        assert ":::" in content
