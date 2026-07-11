"""Configuration file manager for the MkDocs documentation landing page."""

from pathlib import Path

from pyrig.rig.configs.base.badges import BadgesConfigFile
from pyrig.rig.tools.docs_builder import DocsBuilder


class IndexConfigFile(BadgesConfigFile):
    """Configuration manager for the documentation site's landing page.

    Produces the same status badges and description as the badge-augmented
    Markdown base, with the heading replaced by `"Home"` so the auto-generated
    MkDocs nav shows a short label for the landing page.
    """

    def lines(self) -> list[str]:
        """Build the landing page content lines.

        Replaces the inherited project-name heading with `"Home"`.

        Returns:
            Markdown lines for the landing page.
        """
        lines = super().lines()
        lines[0] = "# Home"
        return lines

    def parent_path(self) -> Path:
        """Return the MkDocs documentation source directory."""
        return DocsBuilder.I.docs_dir()

    def stem(self) -> str:
        """Return the filename stem `"index"`."""
        return "index"
