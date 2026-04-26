"""Manage the GitHub issue template chooser configuration file."""

from pathlib import Path

from pyrig.core.strings import read_text_utf8
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

    def is_correct(self) -> bool:
        """Return whether the config file exists and contains content.

        Overrides ``ConfigFile.is_correct()`` to use a simpler content-presence
        check instead of verifying that the required keys from ``_configs()``
        are present. Any non-empty file is accepted as valid, which allows the
        file to be freely customized.

        Note:
            Unlike the default ``is_correct()``, an empty file is treated as
            incorrect rather than as a user opt-out. The file must have at
            least some non-whitespace content to be considered valid.

        Returns:
            ``True`` if the file exists and contains non-whitespace content.
        """
        return self.path().exists() and bool(read_text_utf8(self.path()).strip())

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
