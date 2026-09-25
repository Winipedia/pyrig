"""Wrapper around the check-json JSON syntax linter tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.formatting.json import JSONFormatter
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class JSONLinter(CheckHookTool):
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
        """Return no package dependency; prek provides this built-in hook."""
        return ()

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

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for validating JSON syntax.

        Runs after JSON formatting so it checks the final JSON contents.

        Returns:
            Hook metadata dict for `check-json`.
        """
        return VersionControlHookManager.I.builtin_hook(
            self.check_json,
            priority=VersionControlHookManager.I.deprioritize(
                JSONFormatter.I.format_hook(),
            ),
        )

    def check_json(self) -> Args:
        """Return arguments for the built-in hook.

        Returns:
            Arguments passed to `check-json`.
        """
        return Args()
