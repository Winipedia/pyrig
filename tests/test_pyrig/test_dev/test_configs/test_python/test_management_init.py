"""module."""

from pyrig.dev import management
from pyrig.dev.configs.python.management_init import ManagementInitConfigFile


class TestManagementInitConfigFile:
    """Test class."""

    def test_get_priority(self) -> None:
        """Test method."""
        assert ManagementInitConfigFile.get_priority() > 0

    def test_get_src_module(self) -> None:
        """Test method."""
        assert ManagementInitConfigFile.get_src_module() is management
