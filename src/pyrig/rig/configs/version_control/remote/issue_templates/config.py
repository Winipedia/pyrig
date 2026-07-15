"""Configuration file management for the GitHub issue template chooser."""

from typing import Any

from pyrig.rig.configs.base.issue_template import IssueTemplateConfigFile


class ConfigConfigFile(IssueTemplateConfigFile):
    """Config file for `.github/ISSUE_TEMPLATE/config.yml`.

    Controls GitHub's issue template chooser. The required configuration
    disables blank issues, requiring contributors to pick one of the
    provided issue templates when opening a new issue.
    """

    def stem(self) -> str:
        """Return `"config"` as the filename stem."""
        return "config"

    def _configs(self) -> dict[str, Any]:
        """Return `{"blank_issues_enabled": False}`."""
        return {"blank_issues_enabled": False}
