"""Wrapper around the ryl YAML linter tool."""

from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class YAMLLinter(Tool):
    """Type-safe wrapper for the ryl YAML linter.

    Constructs ryl command-line arguments for linting and auto-fixing YAML
    files.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for ryl."""
        return "https://img.shields.io/badge/YAML-ryl-red"

    def link_url(self) -> str:
        """Return the URL of the ryl project page."""
        return "https://github.com/owenlamont/ryl"

    def name(self) -> str:
        """Return `'ryl'`, the executable name for this tool's CLI command."""
        return "ryl"

    def check_fix_args(self, *args: str) -> Args:
        """Construct ryl check arguments with auto-fix enabled.

        Args:
            *args: Additional arguments forwarded to `ryl check --fix`.

        Returns:
            Args for `ryl check --fix`.
        """
        return self.check_args("--fix", *args)

    def check_args(self, *args: str) -> Args:
        """Construct ryl check arguments.

        No custom rule configuration is passed, so ryl runs its own default
        rule set.

        Args:
            *args: Additional arguments forwarded to `ryl check`.

        Returns:
            Args for `ryl check`.
        """
        return self.args("check", Path().as_posix(), "-d", "'extends: default'", *args)
