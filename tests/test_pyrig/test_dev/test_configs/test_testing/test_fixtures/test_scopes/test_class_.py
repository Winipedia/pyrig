"""module."""

from pyrig.dev.configs.testing.fixtures.scopes.class_ import ClassScopeConfigFile
from pyrig.dev.tests.fixtures.scopes import class_


class TestClassScopeConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method."""
        assert ClassScopeConfigFile.get_src_module() == class_
