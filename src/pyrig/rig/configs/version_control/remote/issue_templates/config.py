"""Configuration file management for the GitHub issue template chooser."""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.yml import YMLDictConfigFile


class ConfigConfigFile(YMLDictConfigFile):
    """Config file for `.github/ISSUE_TEMPLATE/config.yml`.

    Controls GitHub's issue template chooser. The required configuration
    disables blank issues, requiring contributors to pick one of the
    provided issue templates when opening a new issue.
    """

    def parent_path(self) -> Path:
        """Return `Path(".github/ISSUE_TEMPLATE")`."""
        return Path(".github/ISSUE_TEMPLATE")

    def stem(self) -> str:
        """Return `"config"` as the filename stem."""
        return "config"

    def _configs(self) -> dict[str, Any]:
        """Return `{"blank_issues_enabled": False}`."""
        return {"blank_issues_enabled": False}
