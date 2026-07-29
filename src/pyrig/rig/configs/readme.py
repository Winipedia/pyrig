"""Configuration management for the project's README.md file."""

from pathlib import Path

from pyrig.rig.configs.base.badges import BadgesConfigFile
from pyrig.rig.configs.base.config_file import Priority
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.packages.manager import PackageManager


class ReadmeConfigFile(BadgesConfigFile):
    """README.md configuration manager."""

    def priority(self) -> float:
        """Return a priority higher than `PyprojectConfigFile`'s.

        Guarantees README.md already exists by the time `PyprojectConfigFile`
        validates, since `uv add`/`uv sync` fail to resolve the project while
        the declared `readme` file is missing.
        """
        return Priority.increase(PyprojectConfigFile.I.priority())

    def heading(self) -> str:
        """Return the project name as the heading text."""
        return f"{PackageManager.I.project_name()}"

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `"README"` as the filename stem."""
        return "README"
