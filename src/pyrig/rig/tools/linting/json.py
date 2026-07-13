"""Wrapper around the check-json JSON syntax linter tool."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group


class JSONLinter(FileTool):
    """Type-safe wrapper for the check-json JSON syntax linter.

    Constructs check-json command-line arguments for validating that JSON
    files parse. check-json has no auto-fix mode and no CLI flags beyond
    the files to check, so it only ever reports, never mutates.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for check-json."""
        return f"https://img.shields.io/badge/JSON-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the check-json project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `'check-json'`, the executable name for this tool's CLI command."""
        return "check-json"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return `('pre-commit-hooks',)`, the PyPI package providing `check-json`."""
        return ("pre-commit-hooks",)

    def types(self) -> list[str]:
        """Return the list of file types that `check-json` can lint."""
        return ["json"]

    def check_args(self, *args: str) -> Args:
        """Construct check-json arguments.

        check-json takes no flags of its own; every argument is a file path
        to validate.

        Args:
            *args: Additional arguments forwarded to `check-json`, typically
                the file paths to check.

        Returns:
            Args for `check-json`.
        """
        return self.args(*args)
