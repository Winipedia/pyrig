"""Configuration management for Markdown files.

This module provides the MarkdownConfigFile class
for managing Markdown configuration files.
"""

from pyrig.dev.configs.base.text import TextConfigFile


class MarkdownConfigFile(TextConfigFile):
    """Abstract base class for Markdown configuration files.

    Attributes:
        CONTENT_KEY: Dictionary key used to store file content.
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the Markdown file extension.

        Returns:
            The string "md".
        """
        return "md"
