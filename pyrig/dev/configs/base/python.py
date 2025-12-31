r"""Python source file configuration management.

Provides PythonConfigFile base class for .py files with required content.

Example:
    >>> from pathlib import Path
    >>> from pyrig.dev.configs.base.python import PythonConfigFile
    >>>
    >>> class MyPythonFile(PythonConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path("src")
    ...
    ...     @classmethod
    ...     def get_content_str(cls) -> str:
    ...         return "from typing import Any\nimport sys"
"""

from pyrig.dev.configs.base.text import TextConfigFile


class PythonConfigFile(TextConfigFile):
    """Base class for Python (.py) source files.

    Extends TextConfigFile with "py" extension. Inherits content-based validation.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the .py file
        - `get_content_str`: Required Python code

    See Also:
        pyrig.dev.configs.base.text.TextConfigFile: Parent class
        pyrig.dev.configs.base.py_package.PythonPackageConfigFile: For package files
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Return "py"."""
        return "py"
