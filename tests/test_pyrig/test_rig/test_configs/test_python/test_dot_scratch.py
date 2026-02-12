"""module."""

from pathlib import Path

from pyrig.rig.configs.python.dot_scratch import DotScratchConfigFile


class TestDotScratchConfigFile:
    """Test class."""

    def test_is_correct(self) -> None:
        """Test method."""
        assert DotScratchConfigFile().is_correct()

    def test_filename(self) -> None:
        """Test method."""
        assert DotScratchConfigFile.filename() == ".scratch"

    def test_parent_path(
        self,
    ) -> None:
        """Test method."""
        assert DotScratchConfigFile.parent_path() == Path()

    def test_lines(self) -> None:
        """Test method."""
        lines = DotScratchConfigFile.lines()
        assert isinstance(lines, list)
        for line in lines:
            assert isinstance(line, str)
