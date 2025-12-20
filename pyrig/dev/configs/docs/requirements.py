"""Requirements file manager for requirements.txt for mkdocs actions.

This module provides the RequirementsConfigFile class for creating and
managing the project's requirements.txt file for mkdocs actions.
"""

from pathlib import Path

from pyrig.dev.configs.base.base import TxtConfigFile


class RequirementsConfigFile(TxtConfigFile):
    """Configuration file manager for requirements.txt for mkdocs actions.

    Creates a requirements.txt file for mkdocs actions.
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the docs directory path.

        Returns:
            Path to the docs directory.
        """
        return Path("docs")

    @classmethod
    def get_content_str(cls) -> str:
        """Get the requirements content.

        Returns:
            The string "mkdocs-material".
        """
        return "\n".join(cls.get_dependencies())

    @classmethod
    def get_dependencies(cls) -> list[str]:
        """Get the dependencies for the requirements.txt file.

        Returns:
            List of dependencies.
        """
        return ["mkdocs-mermaid2-plugin"]

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the requirements.txt file is valid.

        Returns:
            True if the file contains all required dependencies.
        """
        return super().is_correct() or all(
            dep in cls.get_file_content() for dep in cls.get_dependencies()
        )
