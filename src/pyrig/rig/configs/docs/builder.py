"""Configuration file management for the project's Zensical site."""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.toml import TOMLConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.docs.builder import DocsBuilder
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.controller import VersionController
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class DocsBuilderConfigFile(TOMLConfigFile):
    """Configuration manager for the project's Zensical site (`zensical.toml`).

    Assembles the required configuration from live project metadata.
    """

    def _configs(self) -> dict[str, Any]:
        """Assemble the required `zensical.toml` structure from live project state."""
        branch = VersionController.I.default_branch()
        docs_dir = DocsBuilder.I.docs_dir().as_posix()
        return {
            "project": {
                "site_name": PackageManager.I.project_name(),
                "site_description": PyprojectConfigFile.I.project_description(),
                "site_url": DocsBuilder.I.documentation_url(),
                "repo_url": RemoteVersionController.I.repo_url(),
                "edit_uri": f"edit/{branch}/{docs_dir}",
                "strict": True,
                "validation": {
                    "shadowed_definitions": True,
                    "shadowed_footnotes": True,
                    "unresolved_footnotes": True,
                    "unresolved_references": True,
                    "unused_definitions": True,
                    "unused_footnotes": True,
                },
                "theme": {
                    "features": [
                        "content.action.edit",
                        "content.action.view",
                        "content.code.annotate",
                        "content.code.copy",
                        "content.code.select",
                        "content.footnote.tooltips",
                        "navigation.expand",
                        "navigation.footer",
                        "navigation.indexes",
                        "navigation.instant",
                        "navigation.instant.progress",
                        "navigation.path",
                        "navigation.prune",
                        "navigation.sections",
                        "navigation.top",
                        "navigation.tracking",
                        "search.highlight",
                        "toc.follow",
                    ],
                    "palette": [
                        {
                            "media": "(prefers-color-scheme: light)",
                            "scheme": "default",
                            "toggle": {
                                "icon": "lucide/sun",
                                "name": "Switch to dark mode",
                            },
                        },
                        {
                            "media": "(prefers-color-scheme: dark)",
                            "scheme": "slate",
                            "toggle": {
                                "icon": "lucide/moon",
                                "name": "Switch to light mode",
                            },
                        },
                    ],
                },
                "plugins": {
                    "mkdocstrings": {
                        "handlers": {
                            "python": {
                                "paths": [
                                    PackageManager.I.source_root().as_posix(),
                                ],
                                "inventories": [
                                    "https://docs.python.org/3/objects.inv",
                                ],
                                "options": {
                                    "docstring_options": {
                                        "ignore_init_summary": True,
                                    },
                                    "members": True,
                                    "merge_init_into_class": True,
                                    "scoped_crossrefs": True,
                                    "separate_signature": True,
                                    "show_signature_annotations": True,
                                    "show_signature_type_parameters": True,
                                    "show_submodules": True,
                                    "show_symbol_type_toc": True,
                                    "signature_crossrefs": True,
                                },
                            },
                        },
                    },
                },
            },
        }

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def stem(self) -> str:
        """Return `DocsBuilder.I.name()` as the file stem."""
        return DocsBuilder.I.name()
