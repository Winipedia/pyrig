"""Python test file configuration management.

Provide `PythonTestsConfigFile` base class for test `.py` files with parent path
automatically set to the `tests/` directory.

Example:
    >>> from pyrig.rig.configs.base.py_tests import PythonTestsConfigFile
    >>>
    >>> class MyTestFile(PythonTestsConfigFile):
    ...
    ...     def lines(self) -> list[str]:
    ...     def lines(self) -> list[str]:
    ...
    ...
    ...     def filename(self) -> str:
    ...     def filename(self) -> str:
    >>>
    >>> MyTestFile()  # Creates tests/test_myclass.py
"""

from pathlib import Path

from pyrig.rig.configs.base.python import PythonConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


class PythonTestsConfigFile(PythonConfigFile):
    """Base class for Python test (.py) files.

    Extends `PythonConfigFile` with parent path automatically set to `tests/`.
    Inherits `"py"` extension from `PythonConfigFile`.

    Subclasses must implement:
        - `lines`: Required test code as list of lines
        - `filename`: Test file name (e.g., "test_myclass")

    See Also:
        pyrig.rig.configs.base.python.PythonConfigFile: Parent class
        pyrig.rig.tests.mirror_test.MirrorTestConfigFile: Test naming conventions
    """

    def parent_path(self) -> Path:
        """Return the tests package directory path, typically `Path("tests")`."""
        return Path(MirrorTestConfigFile.I.tests_package_name())

    def parent_path(self) -> Path: