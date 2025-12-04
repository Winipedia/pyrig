"""Configuration for the configs package __init__.py.

This module provides the ConfigsInitConfigFile class for creating
the dev/configs directory structure with an __init__.py file.
All ConfigFile subclasses in this package are automatically discovered.
"""

from types import ModuleType

from pyrig.dev import configs
from pyrig.dev.configs.base.base import InitConfigFile


class ConfigsInitConfigFile(InitConfigFile):
    """Configuration file manager for configs/__init__.py.

    Creates the dev/configs directory with an __init__.py file
    that mirrors pyrig's configs package structure.
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to mirror.

        Returns:
            The pyrig.dev.configs module.
        """
        return configs
