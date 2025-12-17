"""module."""

from pyrig.dev.cli import shared_subcommands
from pyrig.dev.configs.python.shared_subcommands import SharedSubcommandsConfigFile


class TestSharedSubcommandsConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method."""
        module = SharedSubcommandsConfigFile.get_src_module()
        assert module == shared_subcommands
