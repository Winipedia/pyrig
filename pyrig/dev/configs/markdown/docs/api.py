"""Configuration management for docs/api.md files.

Manages docs/api.md with mkdocstrings directive (`:::`) to auto-generate API
documentation from Python docstrings (Google style, source links, inherited members).

See Also:
    mkdocstrings: https://mkdocstrings.github.io/
    pyrig.dev.configs.docs.mkdocs.MkdocsConfigFile
"""

from pathlib import Path

from pyrig.dev.configs.base.markdown import MarkdownConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.management.docs_builder import DocsBuilder


class ApiConfigFile(MarkdownConfigFile):
    """API reference page configuration manager.

    Generates docs/api.md with mkdocstrings directive to auto-generate API
    documentation from Python docstrings. Content: "# API Reference" header
    and `::: project_name` directive.

    Examples:
        Generate docs/api.md::

            ApiConfigFile()

        Generated file::

            # API Reference

            ::: myproject

    See Also:
        pyrig.dev.configs.docs.mkdocs.MkdocsConfigFile
        pyrig.dev.configs.pyproject.PyprojectConfigFile
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for api.md.

        Returns:
            Path: docs directory.
        """
        return DocsBuilder.L.get_docs_dir()

    @classmethod
    def get_lines(cls) -> list[str]:
        """Get the api.md file content.

        Returns:
            List of lines with "# API Reference" and `::: project_name` directive.

        Note:
            Reads project name from pyproject.toml.
        """
        project_name = PyprojectConfigFile.L.get_project_name()
        return ["# API Reference", "", f"::: {project_name}", ""]
