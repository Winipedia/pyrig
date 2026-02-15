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

from pyrig.rig.configs.base.yml import YmlConfigFile
from pyrig.rig.configs.markdown.docs.index import IndexConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class MkdocsConfigFile(YmlConfigFile):
    """MkDocs configuration manager.

    Generates mkdocs.yml with Material theme, dark/light mode toggle, navigation
    (Home, API), search, mermaid diagrams, and mkdocstrings for Google-style
    docstring API documentation.

    Example:
        >>> MkdocsConfigFile.I.validate()

    See Also:
        pyrig.rig.configs.pyproject.PyprojectConfigFile
        pyrig.rig.configs.markdown.docs.index.IndexConfigFile
    """

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def _configs(self) -> dict[str, Any] | list[Any]:
        """Build the complete mkdocs.yml configuration.

        Include Material theme, navigation (Home, API), plugins (search,
        mermaid2, mkdocstrings), and dark/light mode toggle.

        Note:
            The project name is read from pyproject.toml.
        """
        return {
            "site_name": PyprojectConfigFile.I.project_name(),
            "nav": [
                {"Home": IndexConfigFile.I.path().name},
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
