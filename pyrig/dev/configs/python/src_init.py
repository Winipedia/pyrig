"""Adds the src folder with an init file."""

from pathlib import Path
from types import ModuleType

from pyrig import src
from pyrig.dev.configs.base.base import CopyModuleConfigFile
from pyrig.src.modules.module import get_isolated_obj_name


class SrcInitConfigFile(CopyModuleConfigFile):
    """Config file for src/__init__.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return src

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        path = super().get_parent_path()
        # this path will be parent of src
        return path / get_isolated_obj_name(src)

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        return "__init__"
