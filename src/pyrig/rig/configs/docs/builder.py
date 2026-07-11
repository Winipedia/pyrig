"""Configuration file management for the MkDocs site build."""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.yml import YMLDictConfigFile
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.version_control.remote import RemoteVersionController
from pyrig.rig.tools.version_control.version_controller import VersionController


class DocsBuilderConfigFile(YMLDictConfigFile):
    """Configuration manager for the project's MkDocs site (`mkdocs.yml`).

    Assembles the required configuration from live project metadata — name,
    documentation and repository URLs, and default branch — combined with a
    fixed Material theme, strict validation, and the plugins needed to render
    search, Mermaid diagrams, and the API reference from docstrings.
    """

    def _configs(self) -> dict[str, Any]:
        """Assemble the required `mkdocs.yml` structure from live project state.

        Returns:
            Nested dict matching the expected `mkdocs.yml` structure.
        """
        branch = VersionController.I.default_branch()
        docs_dir = DocsBuilder.I.docs_dir().as_posix()
        return {
            "site_name": PackageManager.I.project_name(),
            "site_url": DocsBuilder.I.documentation_url(),
            "repo_url": RemoteVersionController.I.repo_url(),
            "edit_uri": f"edit/{branch}/{docs_dir}",
            "strict": True,
            "validation": {
                "omitted_files": "warn",
                "absolute_links": "warn",
                "unrecognized_links": "warn",
                "anchors": "warn",
            },
            "theme": {
                "name": "material",
                "features": [
                    "content.action.edit",
                    "content.action.view",
                ],
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
            "plugins": [
                "search",
                "mermaid2",
                {
                    "mkdocstrings": {
                        "handlers": {
                            "python": {
                                "options": {
                                    "members": True,
                                    "inherited_members": True,
                                    "show_submodules": True,
                                    "relative_crossrefs": True,
                                    "scoped_crossrefs": True,
                                },
                            },
                        },
                    },
                },
            ],
        }

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def stem(self) -> str:
        """Return `'mkdocs'` as the configuration file stem."""
        return DocsBuilder.I.name()
