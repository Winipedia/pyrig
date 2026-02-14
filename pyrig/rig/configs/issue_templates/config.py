"""Manages issue template chooser config.

Creates .github/ISSUE_TEMPLATE/config.yml which controls the issue template
chooser behavior on GitHub.

See Also:
    https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository
    pyrig.rig.configs.base.yml.YmlConfigFile
"""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.yml import YmlConfigFile


class ConfigConfigFile(YmlConfigFile):
    """Manages .github/ISSUE_TEMPLATE/config.yml.

    Controls the issue template chooser:
    - Whether blank issues are allowed (blank_issues_enabled)

    Example:
        >>> ConfigConfigFile.validate()

    See Also:
        https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository
        pyrig.rig.configs.base.yml.YmlConfigFile
    """

    @classmethod
    def parent_path(cls) -> Path:
        """Return .github/ISSUE_TEMPLATE/."""
        return Path(".github/ISSUE_TEMPLATE")

    @classmethod
    def _configs(cls) -> dict[str, Any]:
        """Return issue template config YAML structure."""
        return {"blank_issues_enabled": False}

    @classmethod
    def is_correct(cls) -> bool:
        """Return True if config.yml exists with content."""
        return cls.path().exists() and bool(
            cls.path().read_text(encoding="utf-8").strip()
        )
