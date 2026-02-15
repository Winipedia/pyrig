"""module."""

from pyrig.rig.cli import subcommands
from pyrig.rig.configs.python.subcommands import SubcommandsConfigFile


class TestSubcommandsConfigFile:
    """Test class."""

    def test_src_module(self) -> None:
        """Test method."""
        module = SubcommandsConfigFile.I.src_module()
        assert module == subcommands
