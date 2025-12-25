"""Configuration for the resources package __init__.py.

This module provides the ResourcesInitConfigFile class for creating
the resources directory structure with an __init__.py file.
"""

from types import ModuleType

from pyrig import resources
from pyrig.dev.configs.base.init import InitConfigFile


class ResourcesInitConfigFile(InitConfigFile):
    """Configuration file manager for resources/__init__.py.

    Creates the resources directory with an __init__.py
    file that mirrors pyrig's resources package structure.
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to mirror.

        Returns:
            The pyrig.resources module.
        """
        return resources
