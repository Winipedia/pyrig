"""Configuration for the builders package __init__.py.

This module provides the BuildersInitConfigFile class for creating
the dev/artifacts/builders directory structure with an __init__.py file.
"""

from types import ModuleType

from pyrig.dev import builders
from pyrig.dev.configs.base.base import InitConfigFile


class BuildersInitConfigFile(InitConfigFile):
    """Configuration file manager for builders/__init__.py.

    Creates the dev/artifacts/builders directory with an __init__.py
    file that mirrors pyrig's builders package structure.
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to mirror.

        Returns:
            The pyrig.dev.builders module.
        """
        return builders
