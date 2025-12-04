"""Config File subclass that creates the builds dir and a build.py."""

from types import ModuleType

from pyrig.dev.artifacts.builders import builder
from pyrig.dev.configs.base.base import InitConfigFile


class BuildersInitConfigFile(InitConfigFile):
    """Config File subclass that creates the dirs folder."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return builder
