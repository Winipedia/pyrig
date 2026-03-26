"""module."""

from pyrig import src
from pyrig.rig.configs.python.src_init import SrcInitConfigFile


class TestSrcInitConfigFile:
    """Test class."""

    def test_create_file(self) -> None:
        """Test method."""

    def test_delete_root_main(self) -> None:
        """Test method."""

    def test_src_module(self) -> None:
        """Test method."""
        module = SrcInitConfigFile.I.src_module()
        assert module == src
