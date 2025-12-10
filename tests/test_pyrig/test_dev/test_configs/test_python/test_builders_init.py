"""Test module."""

from pyrig.dev import builders
from pyrig.dev.configs.python.builders_init import BuildersInitConfigFile


class TestBuildersInitConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method for get_src_module."""
        module = BuildersInitConfigFile.get_src_module()
        assert module == builders
