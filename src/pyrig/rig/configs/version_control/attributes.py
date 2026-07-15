"""Configuration management for `.gitattributes` files."""

from pathlib import Path

from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class VersionControllerAttributesConfigFile(StringConfigFile):
    """Config file manager for `.gitattributes`.

    Declares the git attributes that apply to any project regardless of what
    it does: line-ending normalization, excluding version-control and GitHub
    bookkeeping files from `git archive` output, heading- and def-aware diff
    drivers for Markdown and Python files, and marking the package manager's
    lock file as generated.
    """

    def content(self) -> str:
        """Return the required `.gitattributes` content.

        Returns:
            The baseline attribute rules, followed by a rule marking the
            package manager's lock file as generated, and the rules
            excluding version-control and GitHub metadata from `git
            archive` output.
        """
        return f"""* text=auto eol=lf

*.md diff=markdown
*.py diff=python
*.pyi diff=python

{PackageManager.I.lock_file().as_posix()} linguist-generated=true

.gitattributes  export-ignore
.gitignore      export-ignore
/{RemoteVersionController.I.config_dir().as_posix()}/**     export-ignore
"""

    def extension(self) -> str:
        """Return an empty string, since `.gitattributes` has no extension."""
        return ""

    def extension_separator(self) -> str:
        """Return an empty string, so `.gitattributes` has no trailing dot."""
        return ""

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `'.gitattributes'`, the filename with no extension to split off."""
        return ".gitattributes"
