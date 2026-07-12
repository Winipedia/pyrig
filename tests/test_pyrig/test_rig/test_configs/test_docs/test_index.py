"""module."""

from pathlib import Path

from pyrig.rig.configs.docs.index import IndexConfigFile


class TestIndexConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        assert IndexConfigFile.I.stem() == "index"

    def test_parent_path(self) -> None:
        """Test method."""
        parent_path = IndexConfigFile.I.parent_path()
        assert parent_path == Path("docs")

    def test_heading(self) -> None:
        """Test method."""
        assert IndexConfigFile.I.heading() == "Home"
