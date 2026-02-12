r"""Python source file configuration management.

Provides PythonConfigFile base class for .py files with required content.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.python import PythonConfigFile
    >>>
    >>> class MyPythonFile(PythonConfigFile):
    ...     @classmethod
    ...     def parent_path(cls) -> Path:
    ...         return Path("src")
    ...
    ...     @classmethod
    ...     def get_lines(cls) -> list[str]:
    ...         return ["from typing import Any", "import sys"]
"""

from pyrig.rig.configs.base.string_ import StringConfigFile


class PythonConfigFile(StringConfigFile):
    """Base class for Python (.py) source files.

    Extends StringConfigFile with "py" extension. Inherits content-based validation.

    Subclasses must implement:
        - `parent_path`: Directory containing the .py file
        - `get_lines`: Required Python code as list of lines

    See Also:
        pyrig.rig.configs.base.string_.StringConfigFile: Parent class
        pyrig.rig.configs.base.py_package.PythonPackageConfigFile: For package files
    """

    @classmethod
    def extension(cls) -> str:
        """Return "py"."""
        return "py"
