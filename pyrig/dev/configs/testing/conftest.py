"""Configuration for pytest conftest.py.

Generates tests/conftest.py that imports pyrig's conftest module as pytest plugin,
providing access to pyrig's test fixtures and hooks.

See Also:
    pyrig.dev.tests.conftest
    pytest conftest: https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py
"""

from pyrig.dev.configs.base.py_tests import PythonTestsConfigFile
from pyrig.dev.tests import conftest
from pyrig.src.modules.module import make_obj_importpath


class ConftestConfigFile(PythonTestsConfigFile):
    '''Manages tests/conftest.py.

    Generates conftest.py that imports pyrig's test infrastructure as pytest plugin,
    providing access to pyrig's fixtures, hooks, and test utilities.

    Examples:
        Generate tests/conftest.py::

            ConftestConfigFile()

        Generated file::

            """Pytest configuration for tests.

            This module configures pytest plugins for the test suite...
            """

            pytest_plugins = ["pyrig.dev.tests.conftest"]

    See Also:
        pyrig.dev.tests.conftest
        pyrig.dev.configs.base.py_tests.PythonTestsConfigFile
    '''

    @classmethod
    def get_lines(cls) -> list[str]:
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

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the conftest.py file is valid.

        Returns:
            bool: True if file contains required pytest_plugins import.

        Note:
            Reads file from disk to check content.
        """
        return super().is_correct() or (
            f'pytest_plugins = ["{make_obj_importpath(conftest)}"]'
            in cls.get_file_content()
        )
