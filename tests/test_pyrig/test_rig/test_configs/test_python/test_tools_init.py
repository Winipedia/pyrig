"""module."""

from pyrig.rig import tools
from pyrig.rig.configs.python.tools_init import ToolsInitConfigFile


class TestToolsInitConfigFile:
    """Test class."""

    def test_priority(self) -> None:
        """Test method."""
        assert ToolsInitConfigFile.priority() > 0

    def test_get_src_module(self) -> None:
        """Test method."""
        assert ToolsInitConfigFile.get_src_module() is tools
