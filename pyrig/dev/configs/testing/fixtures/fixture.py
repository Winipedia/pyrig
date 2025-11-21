"""Config file for fixture.py."""

from types import ModuleType

from pyrig.dev.configs.base.base import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.tests.fixtures import fixture


class FixtureConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Config file for fixture.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module."""
        return fixture
