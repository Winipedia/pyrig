"""Configuration file management for the MkDocs site build."""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.yml import YMLDictConfigFile
from pyrig.rig.configs.docs.api import APIDocsConfigFile
from pyrig.rig.configs.docs.index import IndexConfigFile
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.package_manager import PackageManager


class DocsBuilderConfigFile(YMLDictConfigFile):
    """Configuration manager for the project's `mkdocs.yml` file.

    Configures a Material-themed MkDocs site with a dark/light palette
    toggle, navigation to the home and API pages, and search, Mermaid, and
    mkdocstrings plugins.
    """

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def stem(self) -> str:
        """Return `'mkdocs'` as the configuration file stem."""
        return DocsBuilder.I.name()

    def _configs(self) -> dict[str, Any]:
        """Return the required `mkdocs.yml` structure.

        The docstring rendering convention configured for mkdocstrings is
        kept in sync with the convention Ruff enforces.

        Returns:
            The complete `mkdocs.yml` structure as a dict.
        """
        return {
            "site_name": PackageManager.I.project_name(),
            "nav": [
                {
                    "Home": IndexConfigFile.I.path()
                    .relative_to(DocsBuilder.I.docs_dir())
                    .as_posix()
                },
                {
                    "API": APIDocsConfigFile.I.path()
                    .relative_to(DocsBuilder.I.docs_dir())
                    .as_posix()
                },
            ],
            "plugins": [
                "search",
                "mermaid2",
                {
                    "mkdocstrings": {
                        "handlers": {
                            "python": {
                                "options": {
                                    "docstring_style": PythonLinter.I.pydocstyle(),
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
