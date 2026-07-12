"""Configuration management for the project's README.md file.

Manages README.md as a badge-augmented Markdown file at the project root.
"""

from pathlib import Path

from pyrig.rig.configs.base.badges import BadgesConfigFile
from pyrig.rig.tools.package_manager import PackageManager


class ReadmeConfigFile(BadgesConfigFile):
    """README.md configuration manager."""

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `"README"` as the filename stem."""
        return "README"

    def heading(self) -> str:
        """Return the heading text for the project name.

        Returns:
            Heading text to use in the Markdown file.
        """
        return f"{PackageManager.I.project_name()}"
