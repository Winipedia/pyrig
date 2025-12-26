"""Configuration management for docs/api.md files.

This module provides the ApiConfigFile class for creating and
managing the project's docs/api.md file with API reference documentation.
"""

from pathlib import Path

from pyrig.dev.configs.base.markdown import MarkdownConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.package import DOCS_DIR_NAME


class ApiConfigFile(MarkdownConfigFile):
    """Configuration file manager for docs/api.md.

    Creates a docs/api.md file with API reference documentation
    generated from the project's Python docstrings.
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
        """Get the api file content.

        Returns:
            Markdown content with API reference documentation.
        """
        project_name = PyprojectConfigFile.get_project_name()
        return f"""# API Reference

::: {project_name}
"""
