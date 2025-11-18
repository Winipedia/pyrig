"""Config utilities for subcommands.py."""

from types import ModuleType

from pyrig.dev.cli import subcommands
from pyrig.dev.configs.base.base import CopyModuleConfigFile


class SubcommandsConfigFile(CopyModuleConfigFile):
    """Config file for subcommands.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return subcommands

    @classmethod
    def get_content_str(cls) -> str:
        """Get the content."""
        content = super().get_content_str()
        # override content bc we have a subcommnds
        parts = content.split('"""', 2)
        return '"""' + parts[1] + '"""\n'
