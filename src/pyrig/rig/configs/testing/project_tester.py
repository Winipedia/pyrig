"""Configuration for pytest conftest.py.

Generates tests/conftest.py that imports pyrig's conftest module as pytest plugin,
providing access to pyrig's test fixtures and hooks.

See Also:
    pyrig.rig.tests.conftest
    pytest conftest: https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py
"""

from pyrig.rig.configs.base.python_test import PythonTestConfigFile
from pyrig.rig.tests import conftest


class ProjectTesterConfigFile(PythonTestConfigFile):
    '''Manages tests/conftest.py.

    Generates conftest.py that imports pyrig's test infrastructure as pytest plugin,
    providing access to pyrig's fixtures, hooks, and test utilities.

    Examples:
        Generate tests/conftest.py::

            ProjectTesterConfigFile.I.validate()

        Generated file::

            """Pytest configuration for tests.

            This module configures pytest plugins for the test suite...
            """

            pytest_plugins = ["pyrig.rig.tests.conftest"]

    See Also:
        pyrig.rig.tests.conftest
        pyrig.rig.configs.base.py_tests.PythonTestConfigFile
    '''

    def stem(self) -> str:
        """Return the filename stem."""
        return "conftest"

    def lines(self) -> list[str]:
        """Get the conftest.py file content.

        Returns:
            List of lines with docstring and pytest_plugins list.
        """
        return [
            '"""Pytest configuration for tests."""',
            "",
            f'pytest_plugins = ["{conftest.__name__}"]',
            "",
        ]

    def is_correct(self) -> bool:
        """Check if the conftest.py file is valid.

        Returns:
            bool: True if file contains required pytest_plugins import.

        Note:
            Reads file from disk to check content.
        """
        return super().is_correct() or (
            f'pytest_plugins = ["{conftest.__name__}"]' in self.file_content()
        )
