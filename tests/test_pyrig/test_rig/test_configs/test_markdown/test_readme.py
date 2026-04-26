"""Test module."""

from pathlib import Path

from pyrig.rig.configs.markdown.readme import ReadmeConfigFile


class TestReadmeConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        assert ReadmeConfigFile.I.stem() == "README", "Expected README"

    def test_parent_path(self) -> None:
        """Test method."""
        # just assert it returns a path
        assert isinstance(ReadmeConfigFile.I.parent_path(), Path), (
            f"Expected Path, got {type(ReadmeConfigFile.I.parent_path())}"
        )
