"""Configuration for tests/fixtures/__init__.py.

Generates tests/fixtures/__init__.py with pyrig.dev.tests.fixtures docstring for
custom pytest fixtures.

See Also:
    pyrig.dev.tests.fixtures
    pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
"""

from types import ModuleType

from pyrig.dev.configs.base.init import InitConfigFile
from pyrig.dev.tests import fixtures


class FixturesInitConfigFile(InitConfigFile):
    """Manages tests/fixtures/__init__.py.

    Generates tests/fixtures/__init__.py with pyrig.dev.tests.fixtures docstring for
    custom pytest fixtures. Has priority 10 to be created before conftest.py.

    Examples:
        Generate tests/fixtures/__init__.py::

            FixturesInitConfigFile()

        Add custom fixtures::

            # In tests/fixtures/__init__.py
            import pytest

            @pytest.fixture
            def my_custom_fixture():
                return "custom value"

    See Also:
        pyrig.dev.tests.fixtures
        pyrig.dev.configs.testing.conftest.ConftestConfigFile
    """

    @classmethod
    def get_priority(cls) -> float:
        """Get the priority for this config file.

        Returns:
            float: 10.0 (ensures fixtures directory exists before conftest.py uses it).
        """
        return 10

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: pyrig.dev.tests.fixtures module.

        Note:
            Only docstring is copied, no code.
        """
        return fixtures
