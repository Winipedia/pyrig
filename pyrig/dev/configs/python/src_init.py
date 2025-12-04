"""Configuration for the src package __init__.py.

This module provides the SrcInitConfigFile class for creating
the src directory structure with an __init__.py file.
"""

from types import ModuleType

from pyrig import src
from pyrig.dev.configs.base.base import InitConfigFile


class SrcInitConfigFile(InitConfigFile):
    """Configuration file manager for src/__init__.py.

    Creates the src directory with an __init__.py file that
    mirrors pyrig's src package structure.
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to mirror.

        Returns:
            The pyrig.src module.
        """
        return src
