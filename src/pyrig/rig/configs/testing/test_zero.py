"""Configuration for test_zero.py placeholder test.

Generates test_zero.py with empty test_zero() function to ensure pytest runs
successfully even when no other tests exist. Triggers pyrig's scoped fixtures.

See Also:
    pyrig.rig.tests.fixtures
"""

from pathlib import Path
from types import ModuleType

from pyrig.rig.configs.base.copy_module import CopyModuleConfigFile
from pyrig.rig.tests import test_zero
from pyrig.rig.tools.project_tester import ProjectTester


class ZeroTestConfigFile(CopyModuleConfigFile):
    '''Manages test_zero.py.

    Generates test_zero.py with empty test_zero() function to ensure pytest runs
    successfully even when no other tests exist. Triggers pyrig's scoped fixtures.

    Examples:
        Generate test_zero.py::

            ZeroTestConfigFile.I.validate()

        Generated test::

            """Contains an empty test."""

            def test_zero() -> None:
                """Empty test.

                Exists so that when no tests are written yet the base
                fixtures are executed.
                """

    See Also:
        pyrig.rig.tests.fixtures
        pyrig.rig.configs.testing.main_test.MainTestConfigFile
    '''

    def parent_path(self) -> Path:
        """Return the parent directory path as the tests package root."""
        return ProjectTester.I.tests_package_root()

    def copy_module(self) -> ModuleType:
        """Return the module to copy."""
        return test_zero
