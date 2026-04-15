"""Configuration for pytest conftest.py.

Generates tests/conftest.py that imports pyrig's conftest module as pytest plugin,
providing access to pyrig's test fixtures and hooks.

See Also:
    pyrig.rig.tests.conftest
    pytest conftest: https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py
"""

from pathlib import Path
from types import ModuleType

from pyrig.rig.configs.base.copy_module_docstr import CopyModuleOnlyDocstringConfigFile
from pyrig.rig.tests import conftest
from pyrig.rig.tools.project_tester import ProjectTester


class ProjectTesterConfigFile(CopyModuleOnlyDocstringConfigFile):
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
    '''

    def parent_path(self) -> Path:
        """Override to set parent path to the tests package root."""
        return ProjectTester.I.tests_package_root()

    def stem(self) -> str:
        """Return the filename stem."""
        return "conftest"

    def copy_module(self) -> ModuleType:
        """Return the module to copy docstring from."""
        return conftest

    def lines(self) -> list[str]:
        """Get the conftest.py file content.

        Returns:
            List of lines with docstring and pytest_plugins list.
        """
        return [*super().lines(), self.plugin_definition(), ""]

    def is_correct(self) -> bool:
        """Check if the conftest.py file is valid.

        Returns:
            bool: True if file contains required pytest_plugins import.

        Note:
            Reads file from disk to check content.
        """
        return super().is_correct() or (self.plugin_definition() in self.file_content())

    def plugin_definition(self) -> str:
        """Return the pytest_plugins definition line."""
        return f'pytest_plugins = ["{conftest.__name__}"]'
