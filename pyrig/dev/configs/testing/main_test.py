"""Configuration for the test_main.py test file.

This module provides the MainTestConfigFile class for creating
a test file that verifies the CLI entry point works correctly.
"""

from pathlib import Path

from pyrig import main
from pyrig.dev.configs.base.base import PythonPackageConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.module import to_path
from pyrig.src.testing.convention import make_test_obj_importpath_from_obj


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
        test_module_path = to_path(
            make_test_obj_importpath_from_obj(main), is_package=False
        ).parent
        # replace pyrig with project name

        package_name = PyprojectConfigFile.get_package_name()
        test_module_path = Path(
            test_module_path.as_posix().replace("pyrig", package_name, 1)
        )
        return Path(test_module_path)

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
