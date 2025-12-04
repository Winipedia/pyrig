"""module."""

from pyrig.dev.artifacts import resources
from pyrig.dev.configs.python.resources_init import ResourcesInitConfigFile


class TestResourcesInitConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method."""
        module = ResourcesInitConfigFile.get_src_module()
        assert module == resources
