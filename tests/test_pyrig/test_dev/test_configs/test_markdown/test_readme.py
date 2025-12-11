"""Test module."""

from pathlib import Path

from pyrig.dev.configs.markdown.readme import ReadmeConfigFile
from pyrig.src.testing.assertions import assert_with_msg


class TestReadmeConfigFile:
    """Test class."""

    def test_is_correct(self) -> None:
        """Test method."""
        assert ReadmeConfigFile().is_correct()

    def test_get_badges(self) -> None:
        """Test method."""
        badges = ReadmeConfigFile.get_badges()
        assert isinstance(badges, dict), f"Expected dict, got {type(badges)}"
        for badge_category, badge_list in badges.items():
            assert isinstance(badge_category, str), (
                f"Expected string, got {type(badge_category)}"
            )
            assert isinstance(badge_list, list), (
                f"Expected list, got {type(badge_list)}"
            )
            for badge in badge_list:
                assert badge.startswith("[!")

    def test_is_unwanted(self) -> None:
        """Test method."""
        assert not ReadmeConfigFile.is_unwanted()

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
