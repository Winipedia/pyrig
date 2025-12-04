"""module."""

from pyrig import src
from pyrig.dev.configs.python.src_init import SrcInitConfigFile


class TestSrcInitConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method for get_src_module."""
        module = SrcInitConfigFile.get_src_module()
        assert module == src
