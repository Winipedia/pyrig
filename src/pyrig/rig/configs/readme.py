"""Configuration management for the project's README.md file.

Manages README.md as a badge-augmented Markdown file at the project root.
"""

from pathlib import Path

from pyrig.rig.configs.base.badges import BadgesConfigFile
from pyrig.rig.tools.packages.manager import PackageManager


class ReadmeConfigFile(BadgesConfigFile):
    """README.md configuration manager."""

    def heading(self) -> str:
        """Return the project name as the heading text."""
        return f"{PackageManager.I.project_name()}"

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `"README"` as the filename stem."""
        return "README"
