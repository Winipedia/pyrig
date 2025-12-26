"""module."""

from pathlib import Path

from pyrig.dev.configs.markdown.docs.api import ApiConfigFile


class TestApiConfigFile:
    """Test class."""

    def test_get_parent_path(self) -> None:
        """Test method."""
        assert ApiConfigFile.get_parent_path() == Path("docs")

    def test_get_content_str(self) -> None:
        """Test method."""
        assert ":::" in ApiConfigFile.get_content_str()
