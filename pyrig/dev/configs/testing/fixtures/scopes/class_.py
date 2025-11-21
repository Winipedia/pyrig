"""Config file for class_.py."""

from types import ModuleType

from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.tests.fixtures.scopes import class_


class ClassScopeConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Config file for class_.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return class_
