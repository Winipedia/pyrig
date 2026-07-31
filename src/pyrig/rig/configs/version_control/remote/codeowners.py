"""Configuration for the GitHub `CODEOWNERS` file."""

from pathlib import Path

from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.tools.version_control.controller import VersionController
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class CodeownersConfigFile(StringConfigFile):
    """Configuration manager for `.github/CODEOWNERS`.

    Assigns the repository owner as the code owner for every path.
    """

    def content(self) -> str:
        """Return the wildcard ownership rule assigning the repo owner to all paths."""
        return f"* @{VersionController.I.repo_owner()}\n"

    def extension(self) -> str:
        """Return an empty string — CODEOWNERS has no file extension."""
        return ""

    def extension_separator(self) -> str:
        """Return an empty string — no separator is needed without an extension."""
        return ""

    def parent_path(self) -> Path:
        """Return the `RemoteVersionController`'s config directory."""
        return RemoteVersionController.I.config_dir()

    def stem(self) -> str:
        """Return `"CODEOWNERS"`."""
        return "CODEOWNERS"
