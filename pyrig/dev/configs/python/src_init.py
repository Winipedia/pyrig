"""Adds the src folder with an init file."""

from types import ModuleType

from pyrig import src
from pyrig.dev.configs.base.base import InitConfigFile


class SrcInitConfigFile(InitConfigFile):
    """Config file for src/__init__.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return src
