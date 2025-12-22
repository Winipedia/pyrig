"""Configuration management for Python source files.

This module provides the PythonConfigFile class for managing Python source files.
"""

from pyrig.dev.configs.base.text import TextConfigFile


class PythonConfigFile(TextConfigFile):
    """Abstract base class for Python source file configuration.

    Attributes:
        CONTENT_KEY: Dictionary key used to store file content.
    """

    CONTENT_KEY = "content"

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the Python file extension.

        Returns:
            The string "py".
        """
        return "py"
