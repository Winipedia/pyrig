"""Configuration management for README.md files.

This module provides the ReadmeConfigFile class for creating and
managing the project's README.md file with a standard header.
"""

from pathlib import Path

from pyrig.dev.configs.base.base import BadgesMarkdownConfigFile


class ReadmeConfigFile(BadgesMarkdownConfigFile):
    """Configuration file manager for README.md.

    Creates a README.md file with the project name as a header.
    For projects using pyrig, includes a reference link to pyrig.
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the README filename.

        Returns:
            The string "README".
        """
        return "README"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the project root directory.

        Returns:
            Path to the project root.
        """
        return Path()

    @classmethod
    def is_unwanted(cls) -> bool:
        """Check if README is unwanted (always False).

        Returns:
            False, as README.md is always required.
        """
        # README.md is never unwanted
        return False
