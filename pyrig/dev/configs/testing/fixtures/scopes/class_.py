"""Configuration for the class-scoped fixture file.

This module provides the ClassScopeConfigFile class for creating
a class_.py file for class-scoped pytest fixtures.
"""

from types import ModuleType

from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.tests.fixtures.scopes import class_


class ClassScopeConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Configuration file manager for class_.py.

    Creates a class_.py file for fixtures that run once per test class.
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            The pyrig.dev.tests.fixtures.scopes.class_ module.
        """
        return class_
