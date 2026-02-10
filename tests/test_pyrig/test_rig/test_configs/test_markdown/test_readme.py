"""Test module."""

from pathlib import Path

from pyrig.rig.configs.markdown.readme import ReadmeConfigFile


class TestReadmeConfigFile:
    """Test class."""

    def test_is_unwanted(self) -> None:
        """Test method."""
        assert not ReadmeConfigFile.is_unwanted()

    def test_get_filename(self) -> None:
        """Test method for get_filename."""
        assert ReadmeConfigFile.get_filename() == "README", "Expected README"

    def test_get_parent_path(self) -> None:
        """Test method for get_parent_path."""
        # just assert it returns a path
        assert isinstance(ReadmeConfigFile.get_parent_path(), Path), (
            f"Expected Path, got {type(ReadmeConfigFile.get_parent_path())}"
        )
