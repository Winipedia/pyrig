"""Configuration management for docs/api.md files.

Manages docs/api.md with mkdocstrings directive (`:::`) to auto-generate API
documentation from Python docstrings (Google style, source links, inherited members).

See Also:
    mkdocstrings: https://mkdocstrings.github.io/
    pyrig.rig.configs.docs.mkdocs.MkdocsConfigFile
"""

from pathlib import Path

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.docs_builder import DocsBuilder


class ApiConfigFile(MarkdownConfigFile):
    """API reference page configuration manager.

    Generates docs/api.md with mkdocstrings directive to auto-generate API
    documentation from Python docstrings. Content: "# API Reference" header
    and `::: project_name` directive.

    Examples:
        Generate docs/api.md::

            ApiConfigFile.I.validate()

        Generated file::

            # API Reference

            ::: pyrig

    See Also:
        pyrig.rig.configs.docs.mkdocs.MkdocsConfigFile
        pyrig.rig.configs.pyproject.PyprojectConfigFile
    """

    def parent_path(self) -> Path:
        """Get the parent directory for api.md.

        Returns:
            Path: docs directory.
    def parent_path(self) -> Path:
        return DocsBuilder.I.docs_dir()

    def lines(self) -> list[str]:
        """Get the api.md file content.

        Returns:
            list[str]: Lines with "# API Reference" header and
                `::: project_name` mkdocstrings directive.

        Note:
            Reads project name from pyproject.toml.
    def lines(self) -> list[str]:
        project_name = PyprojectConfigFile.I.project_name()
        return ["# API Reference", "", f"::: {project_name}"]
