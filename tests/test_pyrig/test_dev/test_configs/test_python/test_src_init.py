"""module."""

from pathlib import Path

from pyrig import src
from pyrig.dev.configs.python.src_init import SrcInitConfigFile
from pyrig.src.testing.assertions import assert_with_msg


class TestSrcInitConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method for get_src_module."""
        module = SrcInitConfigFile.get_src_module()
        assert module == src

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
