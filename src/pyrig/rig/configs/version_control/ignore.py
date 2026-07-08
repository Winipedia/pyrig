"""Configuration management for `.gitignore` files."""

from pathlib import Path

from pyrig.core.resources import resource_content
from pyrig.rig import resources
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.pyrigger import Pyrigger


class VersionControllerIgnoreConfigFile(StringConfigFile):
    """Config file manager for `.gitignore`.

    Produces the final `.gitignore` content by merging a bundled Python gitignore
    baseline with pyrig-specific additions such as tool caches, build artifacts, and
    the paths of config files that are excluded from version control (e.g. `.env`,
    `.scratch.py`). Additions already present in the baseline are not duplicated.
    """

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `'.gitignore'`, the full filename with no extension to split off."""
        return ".gitignore"

    def extension(self) -> str:
        """Return an empty string, since `.gitignore` has no extension."""
        return ""

    def extension_separator(self) -> str:
        """Return an empty string, so no trailing dot is appended to `.gitignore`."""
        return ""

    def lines(self) -> list[str]:
        """Build the required lines for `.gitignore`.

        Returns:
            The standard gitignore baseline, followed by pyrig-specific
            additions that are not already present in the baseline, followed
            by a trailing empty string.
        """
        standard = self.standard_ignore_lines()
        standard_set = set(standard)
        additional = [
            line for line in self.additional_ignore_lines() if line not in standard_set
        ]
        return [*standard, *additional, ""]

    def additional_ignore_lines(self) -> list[str]:
        """Return the pyrig-specific lines to add to the gitignore baseline.

        Returns:
            A header comment, followed by the version-control-ignore paths
            declared by every tool, followed by the paths of every config
            file that is excluded from version control.
        """
        config_file_paths = (
            cf().path().as_posix()
            for cf in ConfigFile.version_control_ignored_subclasses()
        )
        return [
            f"# {Pyrigger.I.name()} stuff",
            *Tool.subclasses_version_control_ignore_paths(),
            *config_file_paths,
        ]

    def standard_ignore_lines(self) -> list[str]:
        """Return the Python gitignore baseline, split into individual lines."""
        return self.split_lines(self.standard_ignore_text())

    def standard_ignore_text(self) -> str:
        """Return GitHub's canonical Python gitignore template as a single string."""
        return resource_content("GITIGNORE", resources)
