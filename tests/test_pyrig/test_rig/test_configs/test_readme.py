"""Test module."""

from pathlib import Path

from pyrig.rig.configs.readme import ReadmeConfigFile
from pyrig.rig.tools.package_manager import PackageManager


class TestReadmeConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        assert ReadmeConfigFile.I.stem() == "README"

    def test_parent_path(self) -> None:
        """Test method."""
        # just assert it returns a path
        assert isinstance(ReadmeConfigFile.I.parent_path(), Path)

    def test_heading(self) -> None:
        """Test method."""
        assert ReadmeConfigFile.I.heading() == PackageManager.I.project_name()
