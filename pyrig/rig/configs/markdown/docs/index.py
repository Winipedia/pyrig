"""Configuration management for docs/index.md files.

Manages docs/index.md (MkDocs home page) with project name + "Documentation"
header and status badges. Referenced in mkdocs.yml navigation.

See Also:
    pyrig.rig.configs.docs.mkdocs.MkdocsConfigFile
    pyrig.rig.configs.base.badges_md.BadgesMarkdownConfigFile
"""

from pathlib import Path

from pyrig.rig.configs.base.badges_md import BadgesMarkdownConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.docs_builder import DocsBuilder


class IndexConfigFile(BadgesMarkdownConfigFile):
    """MkDocs home page configuration manager.

    Generates docs/index.md with "# {project_name} Documentation" header and
    status badges. Referenced as "Home" page in mkdocs.yml navigation.

    Examples:
        Generate docs/index.md:

            >>> IndexConfigFile.I.validate()

        Header for "myproject":

            # myproject Documentation

    See Also:
        pyrig.rig.configs.docs.mkdocs.MkdocsConfigFile
        pyrig.rig.configs.base.badges_md.BadgesMarkdownConfigFile
    """

    def parent_path(self) -> Path:
        """Return the docs directory path."""
        return DocsBuilder.I.docs_dir()

    def lines(self) -> list[str]:
    def lines(self) -> list[str]:
        Returns:
            Parent directory path.
        """Get the index.md file content.

        Returns:
            Lines with "# {project_name} Documentation" header and badges.

        Note:
            Reads project name from pyproject.toml.
        """
        lines = super().lines()
        project_name = PyprojectConfigFile.I.project_name()
        lines[0] = lines[0].replace(project_name, f"{project_name} Documentation", 1)
        return lines
