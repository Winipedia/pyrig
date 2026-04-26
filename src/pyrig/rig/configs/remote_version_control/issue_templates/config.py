"""Manage the GitHub issue template chooser configuration file."""

from pathlib import Path

from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.yml import DictYmlConfigFile


class ConfigConfigFile(DictYmlConfigFile):
    """Manage ``.github/ISSUE_TEMPLATE/config.yml``.

    Controls GitHub's issue template chooser by generating
    ``.github/ISSUE_TEMPLATE/config.yml``. The default configuration disables
    blank issues, requiring contributors to use one of the provided issue
    templates when opening a new issue.

    Overrides ``is_correct()`` to accept any non-empty file content rather than
    enforcing the exact structure from ``_configs()``. This lets the file be
    customized without being flagged as incorrect.

    Example:
        >>> ConfigConfigFile.I.validate()
    """

    def parent_path(self) -> Path:
        """Return the directory containing the config file.

        Returns:
            Path to ``.github/ISSUE_TEMPLATE``.
        """
        return Path(".github/ISSUE_TEMPLATE")

    def stem(self) -> str:
        """Return the filename stem.

        Returns:
            ``"config"``.
        """
        return "config"

    def _configs(self) -> ConfigDict:
        """Return the YAML configuration structure for the issue template chooser.

        Disables blank issues on GitHub so that contributors must use one of
        the available issue templates when opening a new issue.

        Returns:
            Configuration dict with ``blank_issues_enabled`` set to ``False``.
        """
        return {"blank_issues_enabled": False}
