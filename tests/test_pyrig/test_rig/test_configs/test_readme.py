"""Test module."""

from pathlib import Path

from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.readme import ReadmeConfigFile
from pyrig.rig.tools.packages.manager import PackageManager


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

    def test_priority(self) -> None:
        """Test method."""
        assert ReadmeConfigFile.I.priority() > PyprojectConfigFile.I.priority()
