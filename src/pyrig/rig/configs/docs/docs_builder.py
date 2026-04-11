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

from pyrig.core.types.config_file import ConfigDict
from pyrig.rig.configs.base.yml import DictYmlConfigFile
from pyrig.rig.configs.markdown.docs.index import IndexConfigFile
from pyrig.rig.tools.linter import Linter
from pyrig.rig.tools.package_manager import PackageManager


class DocsBuilderConfigFile(DictYmlConfigFile):
    """MkDocs configuration manager.

    Generates mkdocs.yml with Material theme, dark/light mode toggle, navigation
    (Home, API), search, mermaid diagrams, and mkdocstrings for Google-style
    docstring API documentation.

    Example:
        >>> DocsBuilderConfigFile.I.validate()

    See Also:
        pyrig.rig.configs.pyproject.PyprojectConfigFile
        pyrig.rig.configs.markdown.docs.index.IndexConfigFile
    """

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def stem(self) -> str:
        """Return stem of the configuration file."""
        return "mkdocs"

    def _configs(self) -> ConfigDict:
        """Build the complete mkdocs.yml configuration.

        Include Material theme, navigation (Home, API), plugins (search,
        mermaid2, mkdocstrings), and dark/light mode toggle.

        Note:
            The project name is read from pyproject.toml.
        """
        return {
            "site_name": PackageManager.I.project_name(),
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
                                    "docstring_style": Linter.I.pydocstyle(),
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
