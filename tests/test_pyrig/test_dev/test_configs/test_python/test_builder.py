"""Test module."""

from pyrig.dev.artifacts.builder import builder
from pyrig.dev.configs.python.builder import BuilderConfigFile


class TestBuilderConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method for get_src_module."""
        module = BuilderConfigFile.get_src_module()
        assert module == builder
