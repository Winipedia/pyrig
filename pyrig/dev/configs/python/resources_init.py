"""Config utilities for resources/__init__.py."""

from types import ModuleType

from pyrig.dev.artifacts import resources
from pyrig.dev.configs.base.base import InitConfigFile


class ResourcesInitConfigFile(InitConfigFile):
    """Config file for resources/__init__.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return resources
