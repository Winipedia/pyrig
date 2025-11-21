"""module."""

from pyrig.dev.configs.testing.fixtures.scopes.function import FunctionScopeConfigFile
from pyrig.dev.tests.fixtures.scopes import function


class TestFunctionScopeConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method."""
        assert FunctionScopeConfigFile.get_src_module() == function
