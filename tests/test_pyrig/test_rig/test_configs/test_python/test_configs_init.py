"""module."""

from pyrig.rig import configs
from pyrig.rig.configs.python.configs_init import ConfigsInitConfigFile


class TestConfigsInitConfigFile:
    """Test class."""

    def test_priority(self) -> None:
        """Test method."""
        assert ConfigsInitConfigFile.priority() > 0

    def test_get_src_module(self) -> None:
        """Test method."""
        module = ConfigsInitConfigFile.get_src_module()
        assert module == configs
