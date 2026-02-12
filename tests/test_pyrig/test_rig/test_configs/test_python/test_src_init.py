"""module."""

from pyrig import src
from pyrig.rig.configs.python.src_init import SrcInitConfigFile


class TestSrcInitConfigFile:
    """Test class."""

    def test_src_module(self) -> None:
        """Test method."""
        module = SrcInitConfigFile.src_module()
        assert module == src
