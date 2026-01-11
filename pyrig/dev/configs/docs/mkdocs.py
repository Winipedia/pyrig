"""Configuration file manager for mkdocs.yml.

Manages mkdocs.yml with Material theme, dark/light mode toggle, navigation
(Home, API), search, mermaid diagrams, and mkdocstrings for Google-style
docstring API documentation.

See Also:
    MkDocs: https://www.mkdocs.org/
    Material for MkDocs: https://squidfunk.github.io/mkdocs-material/
    mkdocstrings: https://mkdocstrings.github.io/
"""

from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.yml import YmlConfigFile
from pyrig.dev.configs.markdown.docs.index import IndexConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class MkdocsConfigFile(YmlConfigFile):
    """MkDocs configuration manager.

    Generates mkdocs.yml with Material theme, dark/light mode toggle, navigation
    (Home, API), search, mermaid diagrams, and mkdocstrings for Google-style
    docstring API documentation.

    Examples:
        Generate mkdocs.yml::

            MkdocsConfigFile()

        Build and serve::

            mkdocs build
            mkdocs serve

    See Also:
        pyrig.dev.configs.pyproject.PyprojectConfigFile
        pyrig.dev.configs.markdown.docs.index.IndexConfigFile
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for mkdocs.yml.

        Returns:
            Path: Project root.
        """
        return Path()

    @classmethod
    def _get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the complete mkdocs.yml configuration.

        Generates MkDocs configuration with Material theme, navigation (Home, API),
        plugins (search, mermaid2, mkdocstrings), and dark/light mode toggle.

        Returns:
            dict[str, Any]: Complete mkdocs.yml configuration.

        Note:
            Reads project name from pyproject.toml.
        """
        return {
            "site_name": PyprojectConfigFile.L.get_project_name(),
            "nav": [
                {"Home": IndexConfigFile.L.get_path().name},
                {"API": "api.md"},
            ],
            "plugins": [
                "search",
                "mermaid2",
                {
                    "mkdocstrings": {
                        "handlers": {
                            "python": {
                                "options": {
                                    "docstring_style": "google",
                                    "members": True,
                                    "show_source": True,
                                    "inherited_members": True,
                                    "filters": [],
                                    "show_submodules": True,
                                },
                            },
                        },
                    },
                },
            ],
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
