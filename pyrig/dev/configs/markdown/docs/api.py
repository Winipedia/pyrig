"""Configuration management for docs/api.md files.

This module provides the ApiConfigFile class for creating and managing the
project's docs/api.md file, which serves as the API reference page in the
MkDocs documentation site.

The generated api.md file uses mkdocstrings syntax to automatically generate
API documentation from Python docstrings. The `:::` directive tells mkdocstrings
to extract and render documentation for the entire project package.

The API page includes:
    - All public modules, classes, and functions
    - Docstrings in Google style format
    - Source code links
    - Inherited members
    - Type annotations

See Also:
    mkdocstrings: https://mkdocstrings.github.io/
    pyrig.dev.configs.docs.mkdocs.MkdocsConfigFile
        Configures mkdocstrings plugin
"""

from pathlib import Path

from pyrig.dev.configs.base.markdown import MarkdownConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.package import DOCS_DIR_NAME


class ApiConfigFile(MarkdownConfigFile):
    """Configuration file manager for docs/api.md.

    Generates a docs/api.md file that uses mkdocstrings to automatically
    create API reference documentation from Python docstrings. The file
    contains a simple mkdocstrings directive that extracts documentation
    for the entire project package.

    The generated content is minimal but powerful:
        - Header: "# API Reference"
        - mkdocstrings directive: `::: project_name`

    The mkdocstrings plugin (configured in mkdocs.yml) handles:
        - Extracting docstrings from all modules
        - Rendering in Google style format
        - Adding source code links
        - Showing inherited members
        - Displaying type annotations

    Examples:
        Generate docs/api.md::

            from pyrig.dev.configs.markdown.docs.api import ApiConfigFile

            # Creates docs/api.md
            ApiConfigFile()

        The generated file looks like::

            # API Reference

            ::: myproject

    See Also:
        pyrig.dev.configs.docs.mkdocs.MkdocsConfigFile
            Configures the mkdocstrings plugin
        pyrig.dev.configs.pyproject.PyprojectConfigFile
            Used to get the project name
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for api.md.

        Returns:
            Path: Path to the docs directory.
        """
        return Path(DOCS_DIR_NAME)

    @classmethod
    def get_content_str(cls) -> str:
        """Get the api.md file content.

        Generates minimal Markdown content with a header and mkdocstrings
        directive. The directive tells mkdocstrings to extract and render
        documentation for the entire project package.

        Returns:
            str: Markdown content with "# API Reference" header and
                mkdocstrings directive (`::: project_name`).

        Note:
            This method reads from pyproject.toml to get the project name.

        Examples:
            For a project named "myproject", returns::

                # API Reference

                ::: myproject
        """
        project_name = PyprojectConfigFile.get_project_name()
        return f"""# API Reference

::: {project_name}
"""
