"""Config file for module.py."""

from types import ModuleType

from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.tests.fixtures.scopes import module


class ModuleScopeConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Config file for module.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return module
