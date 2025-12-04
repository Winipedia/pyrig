"""Configuration for the function-scoped fixture file.

This module provides the FunctionScopeConfigFile class for creating
a function.py file for function-scoped pytest fixtures.
"""

from types import ModuleType

from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.tests.fixtures.scopes import function


class FunctionScopeConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Configuration file manager for function.py.

    Creates a function.py file for fixtures that run once per test function.
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            The pyrig.dev.tests.fixtures.scopes.function module.
        """
        return function
