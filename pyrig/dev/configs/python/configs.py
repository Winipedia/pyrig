"""Configs for pyrig.

All subclasses of ConfigFile in the configs package are automatically called.
"""

from types import ModuleType

from pyrig.dev.configs import configs
from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile


class ConfigsConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Config file for configs.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return configs
