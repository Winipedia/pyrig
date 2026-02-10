"""module."""

from pathlib import Path

from pyrig.rig.configs.markdown.docs.index import IndexConfigFile


class TestIndexConfigFile:
    """Test class."""

    def test_get_parent_path(self) -> None:
        """Test method."""
        parent_path = IndexConfigFile.get_parent_path()
        assert parent_path == Path("docs")

    def test_get_lines(self) -> None:
        """Test method."""
        lines = IndexConfigFile.get_lines()
        content_str = "\n".join(lines)
        assert isinstance(content_str, str)
