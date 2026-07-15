"""Wrapper around the check-merge-conflict tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class MergeConflictChecker(Tool):
    """Type-safe wrapper for the pre-commit-hooks merge conflict marker checker."""

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
        """Return the package providing `check-merge-conflict`."""
        return ("pre-commit-hooks",)

    def check_args(self, *args: str) -> Args:
        """Construct check-merge-conflict arguments.

        Unlike `SpellChecker`, this tool has no autofix mode: a leftover
        conflict marker means the merge itself was never actually resolved,
        so there's no safe automatic fix, only a report.

        Args:
            *args: Additional arguments forwarded to `check-merge-conflict`,
                typically the file paths to check.

        Returns:
            Args for `check-merge-conflict`.
        """
        return self.args(*args)

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the merge conflict marker check hook.

        Returns:
            `check_merge_conflict_hook`, wrapped in a single-element tuple.
        """
        return (self.check_merge_conflict_hook(),)

    def check_merge_conflict_hook(self) -> dict[str, Any]:
        """Return the hook metadata for checking for merge conflict markers.

        Ties its priority to `TypeChecker.check_types_hook` so it runs
        alongside the rest of the checks tier rather than after it.

        Returns:
            Hook metadata dict for `check-merge-conflict`.
        """
        return VersionControlHookManager.I.hook(
            self.check_merge_conflict,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_types_hook(),
            ),
            types=["text"],
        )

    def check_merge_conflict(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `check-merge-conflict`.
        """
        return self.check_args()
