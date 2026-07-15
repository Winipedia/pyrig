"""Wrapper around the check-json JSON syntax linter tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hook_manager import VersionControlHookManager


class JSONLinter(Tool):
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

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the JSON validation hook.

        Returns:
            `check_json_hook`, wrapped in a single-element tuple.
        """
        return (self.check_json_hook(),)

    def check_json_hook(self) -> dict[str, Any]:
        """Return the hook metadata for validating JSON syntax.

        Ties its priority to `TypeChecker.check_types_hook` so it runs
        alongside the rest of the checks tier rather than after it.

        Returns:
            Hook metadata dict for `check-json`.
        """
        return VersionControlHookManager.I.hook(
            self.check_json,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_types_hook(),
            ),
            types=["json"],
        )

    def check_json(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `check-json`.
        """
        return self.check_args()
