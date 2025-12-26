'''Configuration management for Python test files.

This module provides the PythonTestsConfigFile class for managing Python test
files in the tests directory. This is a convenience base class that automatically
places files in the tests/ directory.

PythonTestsConfigFile simplifies test file creation by:
- Automatically setting the parent path to tests/
- Inheriting all text-based validation from PythonConfigFile
- Allowing required test boilerplate to be enforced

Example:
    >>> from pyrig.dev.configs.base.py_tests import PythonTestsConfigFile
    >>>
    >>> class MyTestFile(PythonTestsConfigFile):
    ...     @classmethod
    ...     def get_content_str(cls) -> str:
    ...         return """Test module docstring."""
    ...                import pytest
    ...                from mypackage import MyClass
    ...                """
    ...
    ...     @classmethod
    ...     def get_filename(cls) -> str:
    ...         return "test_myclass"
    >>>
    >>> MyTestFile()  # Creates tests/test_myclass.py
'''

from pathlib import Path

from pyrig.dev.configs.base.python import PythonConfigFile
from pyrig.src.testing.convention import TESTS_PACKAGE_NAME


class PythonTestsConfigFile(PythonConfigFile):
    """Abstract base class for Python test files in the tests directory.

    Extends PythonConfigFile to automatically place files in the tests/
    directory. This is a convenience class that saves you from having to
    implement get_parent_path() for every test file.

    The parent path is always Path(TESTS_PACKAGE_NAME), which is typically
    "tests".

    Subclasses must implement:
        - `get_content_str`: Required test code that must be present
        - `get_filename`: Test file name (e.g., "test_myclass")

    Example:
        >>> from pyrig.dev.configs.base.py_tests import PythonTestsConfigFile
        >>>
        >>> class MyTestFile(PythonTestsConfigFile):
        ...     @classmethod
        ...     def get_content_str(cls) -> str:
        ...         return "import pytest"
        ...
        ...     @classmethod
        ...     def get_filename(cls) -> str:
        ...         return "test_example"

    See Also:
        pyrig.dev.configs.base.python.PythonConfigFile: Parent class
        pyrig.src.testing.convention.TESTS_PACKAGE_NAME: Tests directory name
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the tests directory path.

        Returns the path to the tests package directory. This is always
        Path(TESTS_PACKAGE_NAME), which is typically "tests".

        Returns:
            Path to the tests package (typically Path("tests")).

        Example:
            For any PythonTestsConfigFile subclass::

                get_parent_path() -> Path("tests")
                get_filename() -> "test_example"
                get_file_extension() -> "py"
                get_path() -> Path("tests/test_example.py")

        Note:
            This method is already implemented, so subclasses don't need to
            override it unless they want to place tests in a subdirectory.
        """
        return Path(TESTS_PACKAGE_NAME)
