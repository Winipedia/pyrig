"""Config utilities for subcommands.py."""

from types import ModuleType

from pyrig.dev.cli import subcommands
from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile


class SubcommandsConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Config file for subcommands.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return subcommands
