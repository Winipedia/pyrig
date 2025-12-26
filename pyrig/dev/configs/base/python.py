'''Configuration management for Python source files.

This module provides the PythonConfigFile class for managing Python source files
(.py files) that require specific content but allow user extensions.

PythonConfigFile is useful for:
- Creating Python files with required imports or boilerplate
- Ensuring specific functions or classes are present
- Maintaining consistent file headers across a project

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
    ...         return """Module docstring."""
    ...                from typing import Any
    ...                import sys
    ...                """
'''

from pyrig.dev.configs.base.text import TextConfigFile


class PythonConfigFile(TextConfigFile):
    """Abstract base class for Python source file configuration.

    Extends TextConfigFile to use the "py" file extension. All functionality
    is inherited from TextConfigFile - only the extension differs.

    This class is useful for creating Python files with required content
    (imports, boilerplate, etc.) while allowing users to add their own code.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the .py file
        - `get_content_str`: Required Python code that must be present

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
        ...         return "from typing import Any"

    See Also:
        pyrig.dev.configs.base.text.TextConfigFile: Parent class with full docs
        pyrig.dev.configs.base.py_package.PythonPackageConfigFile: For package files
    """

    CONTENT_KEY = "content"

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the Python file extension.

        Returns:
            The string "py" (without the leading dot).

        Example:
            For a class named MyModuleConfigFile::

                get_filename() -> "my_module"
                get_file_extension() -> "py"
                get_path() -> Path("my_module.py")
        """
        return "py"
