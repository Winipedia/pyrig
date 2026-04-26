"""Configuration for the generated ``tests/conftest.py`` file.

Manages a conftest file that registers pyrig's test infrastructure as a
pytest plugin, giving the target project access to pyrig's fixtures and
hooks without explicit imports in each test file.
"""

from pathlib import Path
from types import ModuleType

from pyrig.rig.configs.base.copy_module_docstring import CopyModuleDocstringConfigFile
from pyrig.rig.tests import conftest
from pyrig.rig.tools.project_tester import ProjectTester


class ProjectTesterConfigFile(CopyModuleDocstringConfigFile):
    r"""Generates ``tests/conftest.py`` for the target project.

    The generated file has two parts: the module-level docstring of
    ``pyrig.rig.tests.conftest`` as its own module docstring, followed by a
    ``pytest_plugins`` assignment that registers that module as a pytest plugin.
    This gives the target project automatic access to all of pyrig\'s test
    fixtures and hooks without needing explicit imports in each test file.

    Example:
        Generate or update ``tests/conftest.py``::

            ProjectTesterConfigFile.I.validate()
    """

    def parent_path(self) -> Path:
        """Return the root directory of the tests package.

        Returns:
            Path to the tests package root, e.g. ``Path("tests")``.
        """
        return ProjectTester.I.tests_package_root()

    def stem(self) -> str:
        """Return the filename stem for the generated file.

        Returns:
            ``'conftest'``
        """
        return "conftest"

    def copy_module(self) -> ModuleType:
        """Return the source module whose docstring is written to the generated file.

        Returns:
            ``pyrig.rig.tests.conftest``
        """
        return conftest

    def lines(self) -> list[str]:
        """Return the content of the generated conftest.py as a list of lines.

        Extends the parent output (the conftest module's docstring) with the
        ``pytest_plugins`` assignment and a trailing blank line.

        Returns:
            Lines comprising the module docstring followed by the
            ``pytest_plugins`` assignment.
        """
        return [*super().lines(), self.plugin_definition(), ""]

    def is_correct(self) -> bool:
        """Return whether the generated conftest.py is considered valid.

        The file is valid if the ``pytest_plugins`` assignment is already
        present in the file on disk.

        Returns:
            ``True`` if the ``pytest_plugins`` assignment is present in the
            file on disk.
        """
        return self.plugin_definition() in self.read_content()

    def plugin_definition(self) -> str:
        """Return the ``pytest_plugins`` assignment line for the generated file.

        Returns:
            String of the form ``'pytest_plugins = ["<conftest_module_name>"]'``.
        """
        return f'pytest_plugins = ["{conftest.__name__}"]'
