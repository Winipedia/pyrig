"""Configuration for the test_main.py test file.

This module provides the MainTestConfigFile class for creating a test file
that verifies the CLI entry point works correctly.

The generated test:
    - Tests the main CLI entry point
    - Uses the main_test_fixture from pyrig's test infrastructure
    - Ensures the CLI can be invoked without errors
    - Follows pytest naming conventions

The test file is placed in tests/test_{package_name}/test_main.py to mirror
the project structure.

See Also:
    pyrig.dev.tests.fixtures
        Provides the main_test_fixture used in the test
    pyrig.main
        The CLI entry point being tested
"""

from pathlib import Path

import pyrig
from pyrig import main
from pyrig.dev.configs.base.py_package import PythonPackageConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.path import ModulePath
from pyrig.src.testing.convention import (
    TEST_MODULE_PREFIX,
    make_test_obj_importpath_from_obj,
)


class MainTestConfigFile(PythonPackageConfigFile):
    '''Configuration file manager for test_main.py.

    Generates a test_main.py file that verifies the CLI entry point works
    correctly. The test uses pyrig's main_test_fixture to ensure the CLI
    can be invoked without errors.

    The test file:
        - Is placed in tests/test_{package_name}/test_main.py
        - Contains a test_main() function
        - Uses the main_test_fixture from pyrig's test infrastructure
        - Verifies the CLI entry point is functional

    Path Resolution:
        The file path is determined by:
        1. Getting the test import path for pyrig.main
        2. Replacing "test_pyrig" with "test_{package_name}"
        3. Converting to a file path

    Examples:
        Generate test_main.py::

            from pyrig.dev.configs.testing.main_test import MainTestConfigFile

            # Creates tests/test_myproject/test_main.py
            MainTestConfigFile()

        The generated test looks like::

            """test module."""

            def test_main(main_test_fixture: None) -> None:
                """Test func for main."""
                assert main_test_fixture is None

    See Also:
        pyrig.dev.tests.fixtures
            Provides the main_test_fixture
        pyrig.main
            The CLI entry point being tested
        pyrig.src.testing.convention
            Test naming conventions
    '''

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory path for test_main.py.

        Determines the path by:
        1. Getting the test import path for pyrig.main
           (e.g., tests.test_pyrig.test_main)
        2. Replacing "test_pyrig" with "test_{package_name}"
        3. Converting to a file path
        4. Returning the parent directory

        Returns:
            Path: Parent directory path (e.g., tests/test_myproject/).

        Examples:
            For a project named "myproject"::

                >>> MainTestConfigFile.get_parent_path()
                PosixPath('tests/test_myproject')
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
            str: The string "test_main" (extension .py is added by parent class).
        """
        return "test_main"

    @classmethod
    def get_content_str(cls) -> str:
        '''Get the test file content.

        Generates Python code with a test_main() function that uses the
        main_test_fixture from pyrig's test infrastructure.

        Returns:
            str: Python code with test_main() function.

        Examples:
            Returns::

                """test module."""

                def test_main(main_test_fixture: None) -> None:
                    """Test func for main."""
                    assert main_test_fixture is None
        '''
        return '''"""test module."""


def test_main(main_test_fixture: None) -> None:
    """Test func for main."""
    assert main_test_fixture is None
'''

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the test file is valid.

        Validates that the file contains a test_main function. Allows user
        modifications as long as the core test function is present.

        Returns:
            bool: True if the file contains "def test_main", False otherwise.

        Note:
            This method reads the file from disk to check its content.
        """
        return super().is_correct() or "def test_main" in cls.get_file_content()
