"""module."""

from pathlib import Path

from pyrig.dev.configs.markdown.docs.index import IndexConfigFile


class TestIndexConfigFile:
    """Test class."""

    def test_get_parent_path(self) -> None:
        """Test method."""
        parent_path = IndexConfigFile.get_parent_path()
        assert parent_path == Path("docs")

    def test_get_content_str(self) -> None:
        """Test method."""
        content_str = IndexConfigFile.get_content_str()
        assert isinstance(content_str, str)
