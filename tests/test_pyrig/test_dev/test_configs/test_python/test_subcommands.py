"""module."""

from pyrig.dev.cli import subcommands
from pyrig.dev.configs.python.subcommands import SubcommandsConfigFile


class TestSubcommandsConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method for get_src_module."""
        module = SubcommandsConfigFile.get_src_module()
        assert module == subcommands

    def test_get_content_str(self) -> None:
        """Test method for get_content_str."""
        content_str = SubcommandsConfigFile.get_content_str()
        assert len(content_str) > 0
