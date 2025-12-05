"""Configuration for the fixture.py base fixture file.

This module provides the FixtureConfigFile class for creating
a fixture.py file where users can define custom test fixtures.
"""

from types import ModuleType

from pyrig.dev.configs.base.base import InitConfigFile
from pyrig.dev.tests import fixtures


class FixturesInitConfigFile(InitConfigFile):
    """Configuration file manager for fixture.py.

    Creates a fixture.py file with only the docstring from pyrig's
    fixture module, allowing users to add custom fixtures.
    """

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            The pyrig.dev.tests.fixtures.fixture module.
        """
        return fixtures
