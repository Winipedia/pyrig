"""Wrapper around the check-merge-conflict tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class MergeConflictChecker(CheckHookTool):
    """Type-safe wrapper for prek's pre-commit-hooks-compatible conflict check."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for check-merge-conflict."""
        return f"https://img.shields.io/badge/merge--conflict-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"check-merge-conflict"`, this tool's CLI command name."""
        return "check-merge-conflict"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return no package dependency; prek provides this built-in hook."""
        return ()

    def check_args(self, *args: str) -> Args:
        """Construct check-merge-conflict arguments.

        This checker only reports conflict markers; it has no autofix mode
        because removing a marker could discard unresolved content. The
        `--assume-in-merge` option makes the check run even when Git does not
        report an active merge.

        Args:
            *args: Additional arguments forwarded to `check-merge-conflict`,
                typically the file paths to check.

        Returns:
            Args for `check-merge-conflict`.
        """
        return Args("--assume-in-merge", *args)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for checking for merge conflict markers.

        Runs after the general text-fixing chain.

        Returns:
            Hook metadata dict for `check-merge-conflict --assume-in-merge`.
        """
        return VersionControlHookManager.I.builtin_hook(
            self.check_merge_conflict,
            priority=VersionControlHookManager.I.deprioritize(
                EndOfFileFormatter.I.format_hook(),
            ),
        )

    def check_merge_conflict(self) -> Args:
        """Return arguments for the built-in hook.

        Returns:
            Arguments passed to `check-merge-conflict`.
        """
        return self.check_args()
