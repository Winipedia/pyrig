"""module."""

from pathlib import Path

from pyrig.rig.configs.scratch import ScratchConfigFile


class TestScratchConfigFile:
    """Test class."""

    def test_version_control_ignored(self) -> None:
        """Test method."""
        assert ScratchConfigFile.I.version_control_ignored() is True

    def test_stem(self) -> None:
        """Test method."""
        assert ScratchConfigFile.I.stem() == ".scratch"

    def test_parent_path(
        self,
    ) -> None:
        """Test method."""
        assert ScratchConfigFile.I.parent_path() == Path()

    def test_content(self) -> None:
        """Test method."""
        content = ScratchConfigFile.I.content()
        assert isinstance(content, str)
