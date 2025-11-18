"""Config File subclass that creates the builds dir and a build.py."""

from types import ModuleType

from pyrig.dev.artifacts.builder import builder
from pyrig.dev.configs.base.base import CopyModuleConfigFile


class BuilderConfigFile(CopyModuleConfigFile):
    """Config File subclass that creates the dirs folder."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return builder
