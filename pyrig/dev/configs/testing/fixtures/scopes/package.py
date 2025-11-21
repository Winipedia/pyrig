"""Config file for package.py."""

from types import ModuleType

from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.tests.fixtures.scopes import package


class PackageScopeConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Config file for package.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return package
