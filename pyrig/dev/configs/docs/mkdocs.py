"""Configuration file manager for mkdocs.yml.

This module provides the MkdocsConfigFile class for creating and managing the
project's mkdocs.yml file, which configures MkDocs to generate beautiful
documentation websites from Markdown files and Python docstrings.

The generated mkdocs.yml includes:
    - **Project Metadata**: Site name from pyproject.toml
    - **Material Theme**: Modern, responsive theme with dark/light mode toggle
    - **Navigation**: Home page and API documentation
    - **Search Plugin**: Full-text search across documentation
    - **Mermaid2 Plugin**: Support for Mermaid diagrams in Markdown
    - **mkdocstrings Plugin**: Automatic API documentation from Google-style
      docstrings with source code display and inherited members

The configuration is optimized for Python projects using Google-style docstrings
and provides a professional documentation site out of the box.

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
    """Configuration file manager for mkdocs.yml.

    Generates a complete mkdocs.yml configuration file for building documentation
    websites with MkDocs. The configuration uses the Material theme and includes
    plugins for search, Mermaid diagrams, and automatic API documentation.

    Key Features:
        - **Material Theme**: Modern, responsive design with customizable colors
        - **Dark/Light Mode**: Toggle between dark (slate) and light (default) themes
        - **API Documentation**: Automatic generation from Google-style docstrings
        - **Search**: Full-text search across all documentation
        - **Diagrams**: Mermaid diagram support for visualizations
        - **Source Code**: Links to source code for all documented items

    The generated site includes:
        - Home page (index.md)
        - API documentation (api.md)
        - Search functionality
        - Responsive navigation
        - Syntax highlighting

    Examples:
        Generate mkdocs.yml::

            from pyrig.dev.configs.docs.mkdocs import MkdocsConfigFile

            # Creates mkdocs.yml in project root
            MkdocsConfigFile()

        Build and serve the documentation::

            # Build the site
            mkdocs build

            # Serve locally for development
            mkdocs serve

    See Also:
        pyrig.dev.configs.pyproject.PyprojectConfigFile
            Used to get the project name for site_name
        pyrig.dev.configs.markdown.docs.index.IndexConfigFile
            Generates the home page (index.md)
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for mkdocs.yml.

        Returns:
            Path: Empty Path() representing the project root directory.
        """
        return Path()

    @classmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the complete mkdocs.yml configuration.

        Generates a full MkDocs configuration with Material theme, plugins,
        and navigation structure. The configuration is optimized for Python
        projects using Google-style docstrings.

        Configuration Structure:
            - **site_name**: Project name from pyproject.toml
            - **nav**: Navigation with Home (index.md) and API (api.md) pages
            - **plugins**: Search, Mermaid diagrams, and mkdocstrings for API docs
            - **theme**: Material theme with dark/light mode toggle

        Plugin Details:
            - **search**: Enables full-text search across documentation
            - **mermaid2**: Renders Mermaid diagrams in Markdown
            - **mkdocstrings**: Generates API docs from docstrings with options:
                - docstring_style: "google" (Google-style docstrings)
                - members: True (show all members)
                - show_source: True (link to source code)
                - inherited_members: True (show inherited methods)
                - show_submodules: True (show submodules)

        Theme Configuration:
            - **name**: "material" (Material for MkDocs theme)
            - **palette**: Two schemes with toggle:
                - slate (dark mode) with brightness-4 icon
                - default (light mode) with brightness-7 icon

        Returns:
            dict[str, Any]: Complete mkdocs.yml configuration dictionary.

        Note:
            This method reads from pyproject.toml to get the project name.

        Examples:
            The returned configuration generates a YAML file like::

                site_name: myproject
                nav:
                  - Home: index.md
                  - API: api.md
                plugins:
                  - search
                  - mermaid2
                  - mkdocstrings:
                      handlers:
                        python:
                          options:
                            docstring_style: google
                            members: true
                            show_source: true
                            inherited_members: true
                            show_submodules: true
                theme:
                  name: material
                  palette:
                    - scheme: slate
                      toggle:
                        icon: material/brightness-4
                        name: Light mode
                    - scheme: default
                      toggle:
                        icon: material/brightness-7
                        name: Dark mode
        """
        return {
            "site_name": PyprojectConfigFile.get_project_name(),
            "nav": [
                {"Home": IndexConfigFile.get_path().name},
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
