"""Configuration for the GitHub dependency bot's version updates."""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.yaml import YMLDictConfigFile
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.remote.controller import RemoteVersionController


class DependencyBotConfigFile(YMLDictConfigFile):
    """Configuration manager for `.github/dependabot.yml`.

    Keeps the project's uv dependencies and GitHub Actions dependencies
    updated on a weekly schedule.
    """

    def _configs(self) -> dict[str, Any]:
        """Return the required dependency bot configuration."""
        return {
            "version": 2,
            "updates": [
                self.ecosystem_config(PackageManager.I.name()),
                self.ecosystem_config("github-actions"),
            ],
        }

    def ecosystem_config(
        self,
        package_ecosystem: str,
        directory: str = "/",
        schedule: dict[str, Any] | None = None,
        cooldown: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return the update configuration for an ecosystem."""
        if schedule is None:
            schedule = {"interval": "weekly"}
        if cooldown is None:
            cooldown = {"default-days": 7}
        return {
            "package-ecosystem": package_ecosystem,
            "directory": directory,
            "schedule": schedule,
            "cooldown": cooldown,
        }

    def parent_path(self) -> Path:
        """Return the `RemoteVersionController`'s config directory."""
        return RemoteVersionController.I.dependency_bot_path().parent

    def stem(self) -> str:
        """Return `"dependabot"`, GitHub's required filename stem."""
        return RemoteVersionController.I.dependency_bot_path().stem
