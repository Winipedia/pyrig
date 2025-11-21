"""Config file for session.py."""

from types import ModuleType

from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.tests.fixtures.scopes import session


class SessionScopeConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Config file for session.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return session
