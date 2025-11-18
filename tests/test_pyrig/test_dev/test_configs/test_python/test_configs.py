"""module."""

from pyrig.dev.configs import configs
from pyrig.dev.configs.python.configs import ConfigsConfigFile


class TestConfigsConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method for get_src_module."""
        module = ConfigsConfigFile.get_src_module()
        assert module == configs
