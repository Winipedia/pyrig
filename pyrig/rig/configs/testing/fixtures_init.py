"""Configuration for tests/fixtures/__init__.py.

Generates tests/fixtures/__init__.py with pyrig.rig.tests.fixtures docstring for
custom pytest fixtures.

See Also:
    pyrig.rig.tests.fixtures
    pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
"""

from types import ModuleType

from pyrig.rig.configs.base.base import Priority
from pyrig.rig.configs.base.init import InitConfigFile
from pyrig.rig.tests import fixtures


class FixturesInitConfigFile(InitConfigFile):
    """Manages tests/fixtures/__init__.py.

    Generates tests/fixtures/__init__.py with pyrig.rig.tests.fixtures docstring for
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
        pyrig.rig.tests.fixtures
        pyrig.rig.configs.testing.conftest.ConftestConfigFile
    """

    @classmethod
    def priority(cls) -> float:
        """Get the priority for this config file.

        Returns:
            float: 10.0 (ensures fixtures directory exists before conftest.py uses it).
        """
        return Priority.LOW

    @classmethod
    def src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: pyrig.rig.tests.fixtures module.

        Note:
            Only docstring is copied, no code.
        """
        return fixtures
