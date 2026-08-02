"""Configuration file manager for the documentation landing page."""

from pathlib import Path

from pyrig.rig.configs.base.badges import BadgesConfigFile
from pyrig.rig.tools.docs.builder import DocsBuilder


class IndexConfigFile(BadgesConfigFile):
    """Configuration manager for the documentation site's landing page.

    Produces the same badges and description as the badge-augmented Markdown
    base, using `"Home"` as the heading so the site's auto-generated nav
    shows a short label for the landing page.
    """

    def heading(self) -> str:
        """Return `"Home"` as the heading text."""
        return "Home"

    def parent_path(self) -> Path:
        """Return the `DocsBuilder`'s documentation source directory."""
        return DocsBuilder.I.docs_dir()

    def stem(self) -> str:
        """Return the filename stem `"index"`."""
        return "index"
