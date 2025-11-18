"""module."""

from pathlib import Path

from pyrig.dev.configs.python.subcommands import SubcommandsConfigFile
from pyrig.src.testing.assertions import assert_with_msg


class TestSubcommandsConfigFile:
    """Test class for SubcommandsConfigFile."""

    def test_get_parent_path(self) -> None:
        """Test method for get_parent_path."""
        # just assert it returns a path
        assert_with_msg(
            isinstance(SubcommandsConfigFile.get_parent_path(), Path),
            "Expected Path",
        )

    def test_get_content_str(self) -> None:
        """Test method for get_content_str."""
        content_str = SubcommandsConfigFile.get_content_str()
        assert_with_msg(
            len(content_str) > 0,
            "Expected non-empty string",
        )
