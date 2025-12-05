"""Configuration management for docs/index.md files.

This module provides the IndexConfigFile class for creating and
managing the project's docs/index.md file with a standard header.
"""

from pathlib import Path

from pyrig.dev.configs.base.base import MarkdownConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.package import DOCS_DIR_NAME


class IndexConfigFile(MarkdownConfigFile):
    """Configuration file manager for docs/index.md.

    Creates a docs/index.md file with a standard header and
    instructions for users to add their own content.
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the docs directory path.

        Returns:
            Path to the docs directory.
        """
        return Path(DOCS_DIR_NAME)

    @classmethod
    def get_content_str(cls) -> str:
        """Get the index file content.

        Returns:
            Markdown content with a standard header and instructions.
        """
        return f"""# {PyprojectConfigFile.get_project_name()} Documentation
"""
