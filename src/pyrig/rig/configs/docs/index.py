"""Configuration file manager for the MkDocs documentation landing page."""

from pathlib import Path

from pyrig.rig.configs.base.badges import BadgesConfigFile
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.package_manager import PackageManager


class IndexConfigFile(BadgesConfigFile):
    """Configuration manager for the documentation site's landing page.

    Produces the same project header, status badges, and description as the
    badge-augmented Markdown base, with the heading naming it as the project's
    documentation rather than the project itself.
    """

    def lines(self) -> list[str]:
        """Build the landing page content lines.

        Renames the inherited heading from the project name alone to the
        project name followed by `" Documentation"`.

        Returns:
            Markdown lines for the landing page.
        """
        lines = super().lines()
        project_name = PackageManager.I.project_name()
        lines[0] = lines[0].replace(project_name, f"{project_name} Documentation", 1)
        return lines

    def parent_path(self) -> Path:
        """Return the MkDocs documentation source directory."""
        return DocsBuilder.I.docs_dir()

    def stem(self) -> str:
        """Return the filename stem `"index"`."""
        return "index"
