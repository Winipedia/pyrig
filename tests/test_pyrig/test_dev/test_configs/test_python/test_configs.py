"""module."""

from pathlib import Path

from pyrig.dev.configs.python.configs import ConfigsConfigFile
from pyrig.src.testing.assertions import assert_with_msg


class TestConfigsConfigFile:
    """Test class for ConfigsConfigFile."""

    def test_get_parent_path(self) -> None:
        """Test method for get_parent_path."""
        # just assert it returns a path

        assert_with_msg(
            isinstance(ConfigsConfigFile.get_parent_path(), Path),
            "Expected Path",
        )

    def test_get_content_str(self) -> None:
        """Test method for get_content_str."""
        content_str = ConfigsConfigFile.get_content_str()
        assert_with_msg(
            len(content_str) > 0,
            "Expected non-empty string",
        )
