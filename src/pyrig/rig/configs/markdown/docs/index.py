"""Configuration file manager for the MkDocs home page (``docs/index.md``).

Produces the project's documentation landing page by extending the
badge-augmented Markdown base with a ``{project_name} Documentation`` H1
header.
"""

from pathlib import Path

from pyrig.rig.configs.base.badges_md import BadgesMarkdownConfigFile
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.package_manager import PackageManager


class IndexConfigFile(BadgesMarkdownConfigFile):
    """Configuration manager for the MkDocs home page (``docs/index.md``).

    Produces ``docs/index.md`` with a ``# {project_name} Documentation`` H1
    header, followed by the grouped status badges and project description
    provided by the badge-augmented Markdown base class. The file is registered
    as the "Home" entry in ``mkdocs.yml`` navigation.

    Example:
        >>> IndexConfigFile.I.validate()
    """

    def parent_path(self) -> Path:
        """Return the ``docs/`` directory path.

        Returns:
            ``Path("docs")`` — the MkDocs documentation source directory,
            relative to the project root.
        """
        return DocsBuilder.I.docs_dir()

    def stem(self) -> str:
        """Return ``"index"`` as the filename stem."""
        return "index"

    def lines(self) -> list[str]:
        """Build the home page content lines.

        Extends the parent's output by appending ``" Documentation"`` to the
        project name in the H1 header, so the heading reads
        ``# {project_name} Documentation`` rather than ``# {project_name}``.
        The remainder of the content — badge rows and project description block
        — is inherited unchanged from the base class.

        Returns:
            List of Markdown lines with the modified H1 header followed by the
            badge rows and project description block.
        """
        lines = super().lines()
        project_name = PackageManager.I.project_name()
        lines[0] = lines[0].replace(project_name, f"{project_name} Documentation", 1)
        return lines
