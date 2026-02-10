"""module."""

from pyrig.rig.cli import shared_subcommands
from pyrig.rig.configs.python.shared_subcommands import SharedSubcommandsConfigFile


class TestSharedSubcommandsConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method."""
        module = SharedSubcommandsConfigFile.get_src_module()
        assert module == shared_subcommands
