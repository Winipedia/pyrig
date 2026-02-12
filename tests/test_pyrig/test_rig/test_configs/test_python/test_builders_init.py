"""Test module."""

from pyrig.rig import builders
from pyrig.rig.configs.python.builders_init import BuildersInitConfigFile


class TestBuildersInitConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method."""
        module = BuildersInitConfigFile.get_src_module()
        assert module == builders
