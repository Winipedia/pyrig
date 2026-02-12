"""module."""

from pyrig import resources
from pyrig.rig.configs.python.resources_init import ResourcesInitConfigFile


class TestResourcesInitConfigFile:
    """Test class."""

    def test_src_module(self) -> None:
        """Test method."""
        module = ResourcesInitConfigFile.src_module()
        assert module == resources
