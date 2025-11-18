"""module."""

from pyrig import main
from pyrig.dev.configs.python.main import MainConfigFile
from pyrig.src.testing.assertions import assert_with_msg


class TestMainConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method for get_src_module."""
        module = MainConfigFile.get_src_module()
        assert module == main

    def test_is_correct(self) -> None:
        """Test method for is_correct."""
        # is_correct should return a boolean
        result = MainConfigFile.is_correct()
        assert_with_msg(
            isinstance(result, bool),
            f"Expected bool, got {type(result)}",
        )
