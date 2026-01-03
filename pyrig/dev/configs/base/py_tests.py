"""Python test file configuration management.

Provides PythonTestsConfigFile for managing test files. Automatically places files
in tests/ directory.

Example:
    >>> from pyrig.dev.configs.base.py_tests import PythonTestsConfigFile
    >>>
    >>> class MyTestFile(PythonTestsConfigFile):
    ...     @classmethod
    ...     def get_lines(cls) -> list[str]:
    ...         return ["import pytest"]
    ...
    ...     @classmethod
    ...     def get_filename(cls) -> str:
    ...         return "test_myclass"
    >>>
    >>> MyTestFile()  # Creates tests/test_myclass.py
"""

from pathlib import Path

from pyrig.dev.configs.base.python import PythonConfigFile
from pyrig.src.testing.convention import TESTS_PACKAGE_NAME


class PythonTestsConfigFile(PythonConfigFile):
    """Base class for Python test files.

    Extends PythonConfigFile with parent path automatically set to tests/.

    Subclasses must implement:
        - `get_lines`: Required test code as list of lines
        - `get_filename`: Test file name (e.g., "test_myclass")

    See Also:
        pyrig.dev.configs.base.python.PythonConfigFile: Parent class
        pyrig.src.testing.convention.TESTS_PACKAGE_NAME: Tests directory name
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Return Path(TESTS_PACKAGE_NAME), typically "tests"."""
        return Path(TESTS_PACKAGE_NAME)
