"""Config file manager for mkdocs.yml.

This module provides the MkdocsConfigFile class for creating and
managing the project's mkdocs.yml file for documentation generation.
"""

from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.base import YmlConfigFile
from pyrig.dev.configs.markdown.docs.index import IndexConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class MkdocsConfigFile(YmlConfigFile):
    """Configuration file manager for mkdocs.yml.

    Creates a mkdocs.yml file with project-specific configuration
    for generating documentation using MkDocs.
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the project root directory.

        Returns:
            Path to the project root.
        """
        return Path()

    @classmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the expected mkdocs.yml configuration.

        Returns:
            Complete configuration dict with project metadata,
            theme, and navigation.
        """
        return {
            "site_name": PyprojectConfigFile.get_project_name(),
            "nav": [
                {"Home": IndexConfigFile.get_path().name},
            ],
            "plugins": ["search", "mermaid2"],
            "theme": {
                "name": "material",
                "palette": [
                    {
                        "scheme": "slate",
                        "toggle": {
                            "icon": "material/brightness-4",
                            "name": "Light mode",
                        },
                    },
                    {
                        "scheme": "default",
                        "toggle": {
                            "icon": "material/brightness-7",
                            "name": "Dark mode",
                        },
                    },
                ],
            },
        }
