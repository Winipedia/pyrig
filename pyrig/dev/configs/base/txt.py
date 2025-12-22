"""Configuration management for txt files.

This module provides the TxtConfigFile class for managing txt configuration files.
"""

from pyrig.dev.configs.base.text import TextConfigFile


class TxtConfigFile(TextConfigFile):
    """Abstract base class for txt configuration files.

    Attributes:
        CONTENT_KEY: Dictionary key used to store file content.
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the txt file extension.

        Returns:
            The string "txt".
        """
        return "txt"
