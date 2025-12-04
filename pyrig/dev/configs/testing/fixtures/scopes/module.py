"""Configuration for the module-scoped fixture file.

This module provides the ModuleScopeConfigFile class for creating
a module.py file for module-scoped pytest fixtures.
"""

from types import ModuleType

from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.tests.fixtures.scopes import module


class ModuleScopeConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Configuration file manager for module.py.

    Creates a module.py file for fixtures that run once per test module.
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            The pyrig.dev.tests.fixtures.scopes.module module.
        """
        return module
