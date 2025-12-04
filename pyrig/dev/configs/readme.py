"""Configuration management for README.md files.

This module provides the ReadmeConfigFile class for creating and
managing the project's README.md file with a standard header.
"""

from pathlib import Path

import pyrig
from pyrig.dev.configs.base.base import TextConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class ReadmeConfigFile(TextConfigFile):
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
    def get_file_extension(cls) -> str:
        """Get the markdown file extension.

        Returns:
            The string "md".
        """
        return "md"

    @classmethod
    def get_content_str(cls) -> str:
        """Generate the README content with project header.

        Returns:
            Markdown content with project name and optional pyrig reference.
        """
        content = f"""# {PyprojectConfigFile.get_project_name()}
"""
        if PyprojectConfigFile.get_project_name() != pyrig.__name__:
            content += f"""
(This project uses [{PyprojectConfigFile.get_project_name_from_pkg_name(pyrig.__name__)}](https://github.com/Winipedia/{pyrig.__name__}))
"""
        return content

    @classmethod
    def is_unwanted(cls) -> bool:
        """Check if README is unwanted (always False).

        Returns:
            False, as README.md is always required.
        """
        # README.md is never unwanted
        return False
