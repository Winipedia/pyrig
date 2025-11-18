"""module."""

from pathlib import Path

from pyrig.dev.configs.python.src_init import SrcInitConfigFile
from pyrig.src.testing.assertions import assert_with_msg


class TestSrcInitConfigFile:
    """Test class for SrcInitConfigFile."""

    def test_get_filename(self) -> None:
        """Test method for get_filename."""
        assert_with_msg(
            SrcInitConfigFile.get_filename() == "__init__",
            "Expected __init__",
        )

    def test_get_parent_path(self) -> None:
        """Test method for get_parent_path."""
        # just assert it returns a path
        assert_with_msg(
            isinstance(SrcInitConfigFile.get_parent_path(), Path),
            "Expected Path",
        )

    def test_get_content_str(self) -> None:
        """Test method for get_content_str."""
        content_str = SrcInitConfigFile.get_content_str()
        assert_with_msg(
            len(content_str) > 0,
            "Expected non-empty string",
        )
        # Verify it contains expected docstring
        assert_with_msg(
            '"""src package."""' in content_str,
            "Expected docstring in content",
        )

    def test_is_correct(self) -> None:
        """Test method for is_correct."""
        # is_correct should return a boolean
        result = SrcInitConfigFile.is_correct()
        assert_with_msg(
            isinstance(result, bool),
            f"Expected bool, got {type(result)}",
        )
