"""Shared subcommands ConfigFile.

This module provides the SharedSubcommandsConfigFile class for creating
a shared_subcommands.py file where users can define custom CLI subcommands
that are available in all pyrig projects.
"""

from types import ModuleType

from pyrig.dev.cli import shared_subcommands
from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile


class SharedSubcommandsConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Configuration file manager for shared_subcommands.py.

    Creates a shared_subcommands.py file with only the docstring from pyrig's
    shared_subcommands module, allowing users to add custom CLI subcommands
    that are available in all pyrig projects.
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            The pyrig.dev.cli.shared_subcommands module.
        """
        return shared_subcommands
