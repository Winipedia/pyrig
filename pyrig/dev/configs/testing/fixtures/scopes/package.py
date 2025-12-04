"""Configuration for the package-scoped fixture file.

This module provides the PackageScopeConfigFile class for creating
a package.py file for package-scoped pytest fixtures.
"""

from types import ModuleType

from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.tests.fixtures.scopes import package


class PackageScopeConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Configuration file manager for package.py.

    Creates a package.py file for fixtures that run once per test package.
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            The pyrig.dev.tests.fixtures.scopes.package module.
        """
        return package
