"""module."""

from pathlib import Path

from pyrig.rig.configs.python.dot_scratch import DotScratchConfigFile


class TestDotScratchConfigFile:
    """Test class."""

    def test_is_correct(self) -> None:
        """Test method."""
        assert DotScratchConfigFile().is_correct()

    def test_get_filename(self) -> None:
        """Test method."""
        assert DotScratchConfigFile.get_filename() == ".scratch"

    def test_get_parent_path(
        self,
    ) -> None:
        """Test method."""
        assert DotScratchConfigFile.get_parent_path() == Path()

    def test_get_lines(self) -> None:
        """Test method."""
        lines = DotScratchConfigFile.get_lines()
        assert isinstance(lines, list)
        for line in lines:
            assert isinstance(line, str)
