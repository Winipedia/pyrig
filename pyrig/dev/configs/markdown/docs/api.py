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
from pyrig.src.modules.package import DOCS_DIR_NAME


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
        return Path(DOCS_DIR_NAME)

    @classmethod
    def get_content_str(cls) -> str:
        """Get the api.md file content.

        Returns:
            str: Markdown with "# API Reference" and `::: project_name` directive.

        Note:
            Reads project name from pyproject.toml.
        """
        project_name = PyprojectConfigFile.get_project_name()
        return f"""# API Reference

::: {project_name}
"""
