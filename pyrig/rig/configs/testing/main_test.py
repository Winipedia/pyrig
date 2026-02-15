"""Configuration for test_main.py test file.

Generates test_main.py that verifies CLI entry point works correctly using
main_test_fixture. Placed in tests/test_{package_name}/test_main.py.

See Also:
    pyrig.rig.tests.fixtures
    pyrig.main
"""

from pathlib import Path

import pyrig
from pyrig import main
from pyrig.rig.configs.base.py_package import PythonPackageConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.src.modules.path import ModulePath


class MainTestConfigFile(PythonPackageConfigFile):
    '''Manages test_main.py.

    Generates test_main.py that verifies CLI entry point works correctly using
    main_test_fixture. Placed in tests/test_{package_name}/test_main.py.

    Examples:
        Generate test_main.py::

            MainTestConfigFile.I.validate()

        Generated test::

            """test module."""

            def test_main(main_test_fixture: None) -> None:
                """Test function."""
                assert main_test_fixture is None

    See Also:
        pyrig.rig.tests.fixtures
        pyrig.main
        pyrig.rig.tests.mirror_test.MirrorTestConfigFile
    '''

    def parent_path(self) -> Path:
        """Get the parent directory path for test_main.py.

        Returns:
            Path: Parent directory (e.g., tests/test_myproject/).

        Note:
            Converts pyrig.main test path to project-specific test path.
    def parent_path(self) -> Path:
        test_obj_importpath = MirrorTestConfigFile.I.test_obj_importpath_from_obj(main)
        # this is now tests.test_pyrig.test_main
        test_module_prefix = MirrorTestConfigFile.I.test_module_prefix()
        test_package_name = test_module_prefix + PyprojectConfigFile.I.package_name()
        test_pyrig_name = test_module_prefix + pyrig.__name__

        test_obj_importpath = test_obj_importpath.replace(
            test_pyrig_name, test_package_name
        )
        # this is now tests.test_project_name.test_main
        test_module_path = ModulePath.module_name_to_relative_file_path(
            test_obj_importpath
        )
        return test_module_path.parent

    def filename(self) -> str:
        """Get the test filename.

        Returns:
            str: "test_main" (extension .py added by parent class).
    def filename(self) -> str:
        return "test_main"

    def lines(self) -> list[str]:
        """Get the test file content.

        Returns:
            List of lines with test_main() function.
    def lines(self) -> list[str]:
        return [
            '"""test module."""',
            "",
            "",
            "def test_main(main_test_fixture: None) -> None:",
            '    """Test function."""',
            "    assert main_test_fixture is None",
            "",
        ]

    def is_correct(self) -> bool:
        """Check if the test file is valid.

        Returns:
            bool: True if file contains "def test_main".

        Note:
            Reads file from disk to check content.
    def is_correct(self) -> bool:
        return super().is_correct() or "def test_main" in self.file_content()
