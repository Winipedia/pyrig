"""Wrapper around the ryl YAML linter tool."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group


class YAMLLinter(FileTool):
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

    def extension(self) -> str:
        """Return `'yaml'`, the primary YAML file extension.

        `regex()` is overridden separately, since it also has to match
        the `.yml` spelling, not just `.yaml`.
        """
        return "yaml"

    def regex(self) -> str:
        """Return a regex matching YAML files."""
        return r"\.ya?ml$"

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
        rule set. No target path is baked in either, since ryl errors on a
        file it doesn't recognize (e.g. a non-YAML file), so callers are
        expected to supply the specific files to check.

        Args:
            *args: Additional arguments forwarded to `ryl check`, typically
                the file paths to check.

        Returns:
            Args for `ryl check -d 'extends: default'`.
        """
        return self.args("check", "-d", "'extends: default'", *args)
