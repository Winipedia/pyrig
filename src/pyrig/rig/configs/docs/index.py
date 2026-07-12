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

    def parent_path(self) -> Path:
        """Return the MkDocs documentation source directory."""
        return DocsBuilder.I.docs_dir()

    def stem(self) -> str:
        """Return the filename stem `"index"`."""
        return "index"

    def heading(self) -> str:
        """Return `"Home"`, replacing the inherited project-name heading.

        Returns:
            `"Home"`.
        """
        return "Home"
