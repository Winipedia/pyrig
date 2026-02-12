"""module."""

from pathlib import Path

from pyrig.rig.configs.markdown.docs.index import IndexConfigFile


class TestIndexConfigFile:
    """Test class."""

    def test_parent_path(self) -> None:
        """Test method."""
        parent_path = IndexConfigFile.parent_path()
        assert parent_path == Path("docs")

    def test_lines(self) -> None:
        """Test method."""
        lines = IndexConfigFile.lines()
        content_str = "\n".join(lines)
        assert isinstance(content_str, str)
