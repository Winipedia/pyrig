"""Configuration management for docs/index.md files.

Manages docs/index.md (MkDocs home page) with project name + "Documentation"
header and status badges. Referenced in mkdocs.yml navigation.

See Also:
    pyrig.dev.configs.docs.mkdocs.MkdocsConfigFile
    pyrig.dev.configs.base.badges_md.BadgesMarkdownConfigFile
"""

from pathlib import Path

from pyrig.dev.configs.base.badges_md import BadgesMarkdownConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.management.docs_builder import DocsBuilder


class IndexConfigFile(BadgesMarkdownConfigFile):
    """MkDocs home page configuration manager.

    Generates docs/index.md with "# {project_name} Documentation" header and
    status badges. Referenced as "Home" page in mkdocs.yml navigation.

    Examples:
        Generate docs/index.md::

            IndexConfigFile()

        Header for "myproject"::

            # myproject Documentation

    See Also:
        pyrig.dev.configs.docs.mkdocs.MkdocsConfigFile
        pyrig.dev.configs.base.badges_md.BadgesMarkdownConfigFile
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for index.md.

        Returns:
            Path: docs directory.
        """
        return DocsBuilder.L.get_docs_dir()

    @classmethod
    def get_lines(cls) -> list[str]:
        """Get the index.md file content.

        Returns:
            List of lines with "# {project_name} Documentation" and badges.

        Note:
            Reads project name from pyproject.toml.
        """
        lines = super().get_lines()
        project_name = PyprojectConfigFile.L.get_project_name()
        lines[0] = lines[0].replace(project_name, f"{project_name} Documentation", 1)
        return lines
