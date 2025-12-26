"""Configuration management for docs/index.md files.

This module provides the IndexConfigFile class for creating and managing the
project's docs/index.md file, which serves as the home page for the MkDocs
documentation site.

The generated index.md file includes:
    - Project name with "Documentation" suffix as the main header
    - Status badges (build, coverage, version, license, Python version)
    - Placeholder content for users to customize

The index.md file is referenced in mkdocs.yml as the "Home" page and serves
as the landing page when users visit the documentation site.

See Also:
    pyrig.dev.configs.docs.mkdocs.MkdocsConfigFile
        References this file in the navigation
    pyrig.dev.configs.base.badges_md.BadgesMarkdownConfigFile
        Provides badge generation functionality
"""

from pathlib import Path

from pyrig.dev.configs.base.badges_md import BadgesMarkdownConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.package import DOCS_DIR_NAME


class IndexConfigFile(BadgesMarkdownConfigFile):
    """Configuration file manager for docs/index.md.

    Generates a docs/index.md file that serves as the home page for the MkDocs
    documentation site. The file includes the project name with "Documentation"
    suffix and status badges.

    The generated content includes:
        - Header: "# {project_name} Documentation"
        - Status badges (build, coverage, version, license, Python version)
        - Placeholder content for customization

    Examples:
        Generate docs/index.md::

            from pyrig.dev.configs.markdown.docs.index import IndexConfigFile

            # Creates docs/index.md
            IndexConfigFile()

        For a project named "myproject", the header will be::

            # myproject Documentation

    See Also:
        pyrig.dev.configs.docs.mkdocs.MkdocsConfigFile
            References this file as the "Home" page in navigation
        pyrig.dev.configs.base.badges_md.BadgesMarkdownConfigFile
            Provides badge generation
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for index.md.

        Returns:
            Path: Path to the docs directory.
        """
        return Path(DOCS_DIR_NAME)

    @classmethod
    def get_content_str(cls) -> str:
        """Get the index.md file content.

        Generates Markdown content with the project name followed by
        "Documentation" as the header, plus status badges.

        Returns:
            str: Markdown content with header "{project_name} Documentation"
                and status badges.

        Note:
            This method reads from pyproject.toml to get the project name.

        Examples:
            For a project named "myproject", returns content starting with::

                # myproject Documentation

                [badges here]
        """
        content = super().get_content_str()
        project_name = PyprojectConfigFile.get_project_name()
        return content.replace(project_name, f"{project_name} Documentation", 1)
