"""Configuration for the tests/fixtures/__init__.py file.

This module provides the FixturesInitConfigFile class for creating a
tests/fixtures/__init__.py file where users can define custom pytest fixtures.

The generated file:
    - Starts with pyrig's fixtures module docstring
    - Provides a clean place for custom fixture definitions
    - Integrates with pytest's fixture discovery
    - Allows project-specific test utilities

See Also:
    pyrig.dev.tests.fixtures
        pyrig's fixtures module with base docstring
    pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
"""

from types import ModuleType

from pyrig.dev.configs.base.init import InitConfigFile
from pyrig.dev.tests import fixtures


class FixturesInitConfigFile(InitConfigFile):
    """Configuration file manager for tests/fixtures/__init__.py.

    Generates a tests/fixtures/__init__.py file with pyrig's fixtures module
    docstring, providing a clean starting point for users to define custom
    pytest fixtures.

    The generated file:
        - Contains only the docstring from pyrig.dev.tests.fixtures
        - Provides a place for project-specific fixtures
        - Integrates with pytest's fixture discovery mechanism
        - Has higher priority (10) to be created before conftest.py

    Benefits:
        - Centralized location for custom fixtures
        - Separation of concerns (fixtures vs tests)
        - Easy to import fixtures in tests
        - Follows pytest best practices

    Examples:
        Generate tests/fixtures/__init__.py::

            from pyrig.dev.configs.testing.fixtures_init import FixturesInitConfigFile

            # Creates tests/fixtures/__init__.py
            FixturesInitConfigFile()

        Add custom fixtures to the generated file::

            # In tests/fixtures/__init__.py
            import pytest

            @pytest.fixture
            def my_custom_fixture():
                return "custom value"

    See Also:
        pyrig.dev.tests.fixtures
            Source module for the docstring
        pyrig.dev.configs.testing.conftest.ConftestConfigFile
            Created after this file (lower priority)
    """

    @classmethod
    def get_priority(cls) -> float:
        """Get the priority for this config file.

        Higher priority files are created first. This file has priority 10 to
        ensure it's created before conftest.py (which has default priority).

        Returns:
            float: Priority value of 10.0 (higher than default).

        Note:
            This ensures the fixtures directory exists before conftest.py
            tries to import from it.
        """
        return 10

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: The pyrig.dev.tests.fixtures module.

        Note:
            Only the docstring is copied; no code is included in the
            generated file.
        """
        return fixtures
