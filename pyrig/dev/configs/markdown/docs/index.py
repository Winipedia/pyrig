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
from pyrig.src.modules.package import DOCS_DIR_NAME


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
        return Path(DOCS_DIR_NAME)

    @classmethod
    def get_content_str(cls) -> str:
        """Get the index.md file content.

        Returns:
            str: Markdown with "# {project_name} Documentation" and badges.

        Note:
            Reads project name from pyproject.toml.
        """
        content = super().get_content_str()
        project_name = PyprojectConfigFile.get_project_name()
        return content.replace(project_name, f"{project_name} Documentation", 1)
