"""Python test file configuration management.

Provide `PythonTestsConfigFile` base class for test `.py` files with parent path
automatically set to the `tests/` directory.

Example:
    >>> from pyrig.rig.configs.base.py_tests import PythonTestsConfigFile
    >>>
    >>> class MyTestFile(PythonTestsConfigFile):
    ...
    ...     def lines(self) -> list[str]:
    ...         return ["import pytest"]
    ...
    ...
    ...     def filename(self) -> str:
    ...         return "test_myclass"
    >>>
    >>> MyTestFile()  # Creates tests/test_myclass.py
"""

from pathlib import Path

from pyrig.rig.configs.base.py_package import PythonPackageConfigFile
from pyrig.rig.tools.project_tester import ProjectTester


class PythonTestsConfigFile(PythonPackageConfigFile):
    """Base class for Python test (.py) files.

    Extends `PythonPackageConfigFile` with parent path automatically set to `tests/`.
    Inherits `"py"` extension from `PythonPackageConfigFile`.

    Subclasses must implement:
        - `lines`: Required test code as list of lines
        - `filename`: Test file name (e.g., "test_myclass")
    """

    def parent_path(self) -> Path:
        """Return the tests package directory path, typically `Path("tests")`."""
        return Path(ProjectTester.I.tests_package_name())
