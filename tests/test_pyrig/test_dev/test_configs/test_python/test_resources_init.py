"""module."""

from pathlib import Path

from pyrig.dev.artifacts import resources
from pyrig.dev.configs.python.resources_init import ResourcesInitConfigFile


class TestResourcesInitConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method."""
        module = ResourcesInitConfigFile.get_src_module()
        assert module == resources

    def test_get_parent_path(self) -> None:
        """Test method."""
        assert isinstance(ResourcesInitConfigFile.get_parent_path(), Path)

    def test_get_filename(self) -> None:
        """Test method."""
        assert ResourcesInitConfigFile.get_filename() == "__init__"
