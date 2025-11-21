"""module."""

from pyrig.dev.configs.testing.fixtures.scopes.module import ModuleScopeConfigFile
from pyrig.dev.tests.fixtures.scopes import module


class TestModuleScopeConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method."""
        assert ModuleScopeConfigFile.get_src_module() == module
