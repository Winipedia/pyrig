"""Configuration for generating the test_zero.py placeholder test file."""

from pathlib import Path
from types import ModuleType

from pyrig.rig.configs.base.copy_module import CopyModuleConfigFile
from pyrig.rig.tests import test_zero as test_zero_module
from pyrig.rig.tests.test_zero import test_zero
from pyrig.rig.tools.project_tester import ProjectTester


class ZeroTestConfigFile(CopyModuleConfigFile):
    """Generates ``test_zero.py`` in the tests package root of a scaffolded project.

    Copies the content of ``pyrig.rig.tests.test_zero`` into the project's
    ``tests/`` directory, replacing the ``pyrig`` package prefix with the target
    project's package name. The result is a ``test_zero.py`` file containing a
    single empty ``test_zero()`` function.

    The generated file serves two purposes:

    - It ensures pytest always collects at least one test, preventing exit
      code 4 (no tests found) in CI pipelines for projects that have not yet
      written any real tests.
    - It triggers session-scoped autouse fixtures on the very first test run.

    Note:
        The class is named ``ZeroTestConfigFile`` rather than
        ``TestZeroConfigFile`` to prevent pytest from collecting it as a test
        class when it is imported into test files.

    Example:
        Generate ``test_zero.py`` for the current project::

            ZeroTestConfigFile.I.validate()
    """

    def parent_path(self) -> Path:
        """Return the tests package root as the destination directory.

        Overrides the base class, which would derive a nested path from
        the source module name (for example ``tests/<pkg>/rig/tests``).
        This override places ``test_zero.py`` directly in the top-level
        ``tests/`` directory, which is where pytest expects to find it.

        Returns:
            ``Path("tests")`` — the root of the project's tests package.
        """
        return ProjectTester.I.tests_package_root()

    def copy_module(self) -> ModuleType:
        """Return the source module whose content is written to the project.

        Returns:
            ``pyrig.rig.tests.test_zero``
        """
        return test_zero_module

    def is_correct(self) -> bool:
        """Conisdered correct if def test_zero() exists in the target file."""
        return f"def {test_zero.__name__}()" in self.file_content()
