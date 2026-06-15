"""Test module."""

from pyrig.rig import resources
from pyrig.rig.configs.base.init import InitConfigFile
from pyrig.rig.utils.configs import resources_init_config_file


def test_resources_init_config_file() -> None:
    """Test function."""
    config_file = resources_init_config_file()
    assert isinstance(config_file, InitConfigFile)
    assert config_file.copy_module() is resources
