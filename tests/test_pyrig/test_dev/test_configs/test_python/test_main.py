"""module."""

from pathlib import Path

from pyrig.dev.configs.python.main import MainConfigFile
from pyrig.src.testing.assertions import assert_with_msg


class TestMainConfigFile:
    """Test class for MainConfigFile."""

    def test_get_parent_path(self) -> None:
        """Test method for get_parent_path."""
        # just assert it returns a path
        assert_with_msg(
            isinstance(MainConfigFile.get_parent_path(), Path),
            "Expected Path",
        )

    def test_get_content_str(self) -> None:
        """Test method for get_content_str."""
        content_str = MainConfigFile.get_content_str()
        assert_with_msg(
            len(content_str) > 0,
            "Expected non-empty string",
        )
        # Verify it contains expected main.py content
        assert_with_msg(
            "def main" in content_str,
            "Expected 'def main' in content",
        )

    def test_is_correct(self) -> None:
        """Test method for is_correct."""
        # is_correct should return a boolean
        result = MainConfigFile.is_correct()
        assert_with_msg(
            isinstance(result, bool),
            f"Expected bool, got {type(result)}",
        )
