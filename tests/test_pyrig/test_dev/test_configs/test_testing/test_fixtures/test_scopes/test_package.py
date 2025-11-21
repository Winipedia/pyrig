"""module."""

from pyrig.dev.configs.testing.fixtures.scopes.package import PackageScopeConfigFile
from pyrig.dev.tests.fixtures.scopes import package


class TestPackageScopeConfigFile:
    """Test class."""

    def test_get_src_module(self) -> None:
        """Test method."""
        assert PackageScopeConfigFile.get_src_module() == package
