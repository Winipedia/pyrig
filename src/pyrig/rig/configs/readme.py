"""Configuration management for the project's README.md file.

Manages README.md as a badge-augmented Markdown file at the project root.
"""

from pathlib import Path

from pyrig.rig.configs.base.badges import BadgesConfigFile


class ReadmeConfigFile(BadgesConfigFile):
    """README.md configuration manager."""

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `"README"` as the filename stem."""
        return "README"
