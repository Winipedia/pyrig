"""Configuration for the test_main.py test file.

This module provides the MainTestConfigFile class for creating
a test file that verifies the CLI entry point works correctly.
"""

from pathlib import Path

import pyrig
from pyrig import main
from pyrig.dev.configs.base.base import PythonPackageConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.path import ModulePath
from pyrig.src.testing.convention import (
    TEST_MODULE_PREFIX,
    make_test_obj_importpath_from_obj,
)


class MainTestConfigFile(PythonPackageConfigFile):
    """Configuration file manager for test_main.py.

    Creates a test file that verifies the CLI entry point
    responds correctly to --help.
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the test directory path.

        Returns:
            Path to the tests/pkg_name/src directory.
        """
        test_obj_importpath = make_test_obj_importpath_from_obj(main)
        # this is now tests.test_pyrig.test_main
        test_package_name = TEST_MODULE_PREFIX + PyprojectConfigFile.get_package_name()
        test_pyrig_name = TEST_MODULE_PREFIX + pyrig.__name__

        test_obj_importpath = test_obj_importpath.replace(
            test_pyrig_name, test_package_name
        )
        # this is now tests.test_project_name.test_main
        test_module_path = ModulePath.module_name_to_relative_file_path(
            test_obj_importpath
        )
        return test_module_path.parent

    @classmethod
    def get_filename(cls) -> str:
        """Get the test filename.

        Returns:
            The string "test_main".
        """
        return "test_main"

    @classmethod
    def get_content_str(cls) -> str:
        """Get the test file content.

        Returns:
            Python code with a test that verifies CLI --help works.
        """
        return '''"""test module."""


def test_main(main_test_fixture: None) -> None:
    """Test func for main."""
    assert main_test_fixture is None
'''

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the test file is valid.

        Allows modifications as long as test_main function exists.

        Returns:
            True if the file contains a test_main function.
        """
        return super().is_correct() or "def test_main" in cls.get_file_content()
