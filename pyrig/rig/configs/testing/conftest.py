"""Configuration for pytest conftest.py.

Generates tests/conftest.py that imports pyrig's conftest module as pytest plugin,
providing access to pyrig's test fixtures and hooks.

See Also:
    pyrig.rig.tests.conftest
    pytest conftest: https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py
"""

from pyrig.rig.configs.base.py_tests import PythonTestsConfigFile
from pyrig.rig.tests import conftest
from pyrig.src.modules.module import make_obj_importpath


class ConftestConfigFile(PythonTestsConfigFile):
    '''Manages tests/conftest.py.

    Generates conftest.py that imports pyrig's test infrastructure as pytest plugin,
    providing access to pyrig's fixtures, hooks, and test utilities.

    Examples:
        Generate tests/conftest.py::

            ConftestConfigFile.I.validate()

        Generated file::

            """Pytest configuration for tests.

            This module configures pytest plugins for the test suite...
            """

            pytest_plugins = ["pyrig.rig.tests.conftest"]

    See Also:
        pyrig.rig.tests.conftest
        pyrig.rig.configs.base.py_tests.PythonTestsConfigFile
    '''

    def lines(self) -> list[str]:
        """Get the conftest.py file content.

        Returns:
            List of lines with docstring and pytest_plugins list.
        """
        return [
            '"""Pytest configuration for tests.',
            "",
            "This defines the pyrig pytest plugin that provides access to pyrig's test",
            "infrastructure, including fixtures, hooks, and test utilities.",
            '"""',
            "",
            f'pytest_plugins = ["{make_obj_importpath(conftest)}"]',
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
            f'pytest_plugins = ["{make_obj_importpath(conftest)}"]'
            in self.file_content()
        )
