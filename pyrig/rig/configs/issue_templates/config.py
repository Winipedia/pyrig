"""Configuration management for issue template chooser config.

Manages .github/ISSUE_TEMPLATE/config.yml which controls the issue template
chooser behavior on GitHub.

See Also:
    https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository
    pyrig.rig.configs.base.yml.YmlConfigFile
"""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.yml import YmlConfigFile


class ConfigConfigFile(YmlConfigFile):
    """Issue template chooser configuration manager.

    Generates .github/ISSUE_TEMPLATE/config.yml which controls:
    - Whether blank issues are allowed (blank_issues_enabled)

    Examples:
        Generate config.yml::

            ConfigConfigFile()

    See Also:
        https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository
        pyrig.rig.configs.base.yml.YmlConfigFile
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for the config.

        Returns:
            Path: .github/ISSUE_TEMPLATE/.
        """
        return Path(".github/ISSUE_TEMPLATE")

    @classmethod
    def _get_configs(cls) -> dict[str, Any]:
        """Get the issue template config.

        Returns:
            dict[str, Any]: Issue template config YAML structure.
        """
        return {"blank_issues_enabled": False}

    @classmethod
    def is_correct(cls) -> bool:
        """Check if config.yml exists and is non-empty.

        Returns:
            bool: True if file exists with content, False otherwise.
        """
        return cls.get_path().exists() and bool(
            cls.get_path().read_text(encoding="utf-8").strip()
        )
