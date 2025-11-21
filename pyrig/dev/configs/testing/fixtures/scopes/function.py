"""Config file for function.py."""

from types import ModuleType

from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.tests.fixtures.scopes import function


class FunctionScopeConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Config file for function.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return function
