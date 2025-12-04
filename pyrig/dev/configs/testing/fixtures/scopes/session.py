"""Configuration for the session-scoped fixture file.

This module provides the SessionScopeConfigFile class for creating
a session.py file for session-scoped pytest fixtures.
"""

from types import ModuleType

from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.tests.fixtures.scopes import session


class SessionScopeConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Configuration file manager for session.py.

    Creates a session.py file for fixtures that run once per test session.
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            The pyrig.dev.tests.fixtures.scopes.session module.
        """
        return session
