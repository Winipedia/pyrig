"""Configuration for the subcommands.py CLI extension file.

This module provides the SubcommandsConfigFile class for creating
a subcommands.py file where users can define custom CLI subcommands.
"""

from types import ModuleType

from pyrig.dev.cli import subcommands
from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile


class SubcommandsConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Configuration file manager for subcommands.py.

    Creates a subcommands.py file with only the docstring from pyrig's
    subcommands module, allowing users to add custom CLI subcommands.
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            The pyrig.dev.cli.subcommands module.
        """
        return subcommands
