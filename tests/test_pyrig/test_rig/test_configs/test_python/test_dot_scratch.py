"""module."""

from pathlib import Path

from pyrig.rig.configs.python.dot_scratch import DotScratchConfigFile


class TestDotScratchConfigFile:
    """Test class."""

    def test_is_correct(self) -> None:
        """Test method."""
        assert DotScratchConfigFile.I.is_correct()

    def test_filename(self) -> None:
        """Test method."""
        assert DotScratchConfigFile.I.filename() == ".scratch"

    def test_parent_path(
        self,
    ) -> None:
        """Test method."""
        assert DotScratchConfigFile.I.parent_path() == Path()

    def test_lines(self) -> None:
        """Test method."""
        lines = DotScratchConfigFile.I.lines()
        assert isinstance(lines, list)
        for line in lines:
            assert isinstance(line, str)
