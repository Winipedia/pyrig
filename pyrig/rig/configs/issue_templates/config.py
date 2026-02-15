"""Manage issue template chooser config.

Create .github/ISSUE_TEMPLATE/config.yml to control the issue template
chooser behavior on GitHub.

See Also:
    https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository
    pyrig.rig.configs.base.yml.YmlConfigFile
"""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.yml import YmlConfigFile


class ConfigConfigFile(YmlConfigFile):
    """Manage .github/ISSUE_TEMPLATE/config.yml.

    Control the issue template chooser:
    - Whether blank issues are allowed (blank_issues_enabled)

    Example:
        >>> ConfigConfigFile.I.validate()

    See Also:
        https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository
        pyrig.rig.configs.base.yml.YmlConfigFile
    """

    def parent_path(self) -> Path:
        """Return .github/ISSUE_TEMPLATE/."""
        return Path(".github/ISSUE_TEMPLATE")

    def _configs(self) -> dict[str, Any]:
        """Return issue template config YAML structure."""
        return {"blank_issues_enabled": False}

    def is_correct(self) -> bool:
        """Return True if config.yml exists with content."""
        return self.path().exists() and bool(
            self.path().read_text(encoding="utf-8").strip()
        )
