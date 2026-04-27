"""Configuration file manager for mkdocs.yml.

Manages the project's mkdocs.yml, which configures the Material-themed
MkDocs site with a dark/light mode palette toggle, page navigation,
Mermaid diagram support, and Google-style API documentation via mkdocstrings.
"""

from pathlib import Path

from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.yml import DictYmlConfigFile
from pyrig.rig.configs.markdown.docs.api import ApiConfigFile
from pyrig.rig.configs.markdown.docs.index import IndexConfigFile
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.package_manager import PackageManager


class DocsBuilderConfigFile(DictYmlConfigFile):
    """Configuration manager for the project's ``mkdocs.yml`` file.

    Generates ``mkdocs.yml`` with the Material theme, a dark/light mode
    palette toggle, navigation entries for the Home and API pages, and
    the search, mermaid2, and mkdocstrings plugins configured for
    Google-style docstring rendering.

    Example:
        >>> DocsBuilderConfigFile.I.validate()
    """

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def stem(self) -> str:
        """Return ``'mkdocs'`` as the configuration file stem."""
        return DocsBuilder.I.name()

    def _configs(self) -> ConfigDict:
        """Build the complete mkdocs.yml configuration.

        Constructs the full configuration dict that is written to
        ``mkdocs.yml``. The returned dict contains four top-level keys:

        - ``site_name``: Set to the current working directory name, which
          by convention matches the project name.
        - ``nav``: Two entries — ``Home`` pointing to ``index.md`` and
          ``API`` pointing to ``api.md``, both expressed as POSIX paths
          relative to the ``docs/`` directory.
        - ``plugins``: Enables ``search``, ``mermaid2``, and
          ``mkdocstrings`` (configured for the Python handler). The
          ``docstring_style`` option is sourced from
          :meth:`~pyrig.rig.tools.linting.python.PythonLinter.pydocstyle` so that
          Ruff and mkdocstrings always agree on the docstring convention.
        - ``theme``: Uses the Material theme with a two-entry palette:
          dark mode (``slate`` scheme) listed first so it is the default,
          followed by light mode (``default`` scheme). Each entry has a
          brightness toggle icon and label for switching between modes.

        Returns:
            A ``ConfigDict`` representing the complete mkdocs.yml structure.
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
                    "API": ApiConfigFile.I.path()
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
