"""Test module."""

from pathlib import Path

from pyrig.dev.configs.readme import ReadmeConfigFile
from pyrig.src.testing.assertions import assert_with_msg


class TestReadmeConfigFile:
    """Test class for ReadmeConfigFile."""

    def test_get_filename(self) -> None:
        """Test method for get_filename."""
        assert_with_msg(
            ReadmeConfigFile.get_filename() == "README",
            "Expected README",
        )

    def test_get_parent_path(self) -> None:
        """Test method for get_parent_path."""
        # just assert it returns a path
        assert_with_msg(
            isinstance(ReadmeConfigFile.get_parent_path(), Path),
            f"Expected Path, got {type(ReadmeConfigFile.get_parent_path())}",
        )

    def test_get_content_str(self) -> None:
        """Test method for get_content_str."""
        content_str = ReadmeConfigFile.get_content_str()
        assert_with_msg(
            isinstance(content_str, str),
            "Expected non-empty string",
        )

    def test_get_file_extension(self) -> None:
        """Test method for get_file_extension."""
        assert_with_msg(
            ReadmeConfigFile.get_file_extension() == "md",
            "Expected md",
        )
