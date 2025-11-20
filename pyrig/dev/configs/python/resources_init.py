"""Config utilities for resources/__init__.py."""

from pathlib import Path
from types import ModuleType

from pyrig.dev.artifacts import resources
from pyrig.dev.configs.base.base import CopyModuleConfigFile
from pyrig.src.modules.module import get_isolated_obj_name


class ResourcesInitConfigFile(CopyModuleConfigFile):
    """Config file for resources/__init__.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return resources

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        path = super().get_parent_path()
        # this path will be parent of resources
        return path / get_isolated_obj_name(resources)

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        return "__init__"
