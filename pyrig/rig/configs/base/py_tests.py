"""Python test file configuration management.

Provides PythonTestsConfigFile for managing test files. Automatically places files
in tests/ directory.

Example:
    >>> from pyrig.rig.configs.base.py_tests import PythonTestsConfigFile
    >>>
    >>> class MyTestFile(PythonTestsConfigFile):
    ...     @classmethod
    ...     def lines(cls) -> list[str]:
    ...         return ["import pytest"]
    ...
    ...     @classmethod
    ...     def filename(cls) -> str:
    ...         return "test_myclass"
    >>>
    >>> MyTestFile()  # Creates tests/test_myclass.py
"""

from pathlib import Path

from pyrig.rig.configs.base.python import PythonConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


class PythonTestsConfigFile(PythonConfigFile):
    """Base class for Python test files.

    Extends PythonConfigFile with parent path automatically set to tests/.

    Subclasses must implement:
        - `lines`: Required test code as list of lines
        - `filename`: Test file name (e.g., "test_myclass")

    See Also:
        pyrig.rig.configs.base.python.PythonConfigFile: Parent class
        pyrig.rig.tests.mirror_test.MirrorTestConfigFile: Test naming conventions
    """

    @classmethod
    def parent_path(cls) -> Path:
        """Return Path(TESTS_PACKAGE_NAME), typically "tests"."""
        return Path(MirrorTestConfigFile.L.tests_package_name())
