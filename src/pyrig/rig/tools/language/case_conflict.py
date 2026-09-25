"""Wrapper around the check-case-conflict tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class CaseConflictChecker(CheckHookTool):
    """Type-safe wrapper for prek's pre-commit-hooks-compatible case checker."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for check-case-conflict."""
        return f"https://img.shields.io/badge/case--conflict-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"check-case-conflict"`, this tool's CLI command name."""
        return "check-case-conflict"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return no package dependency; prek provides this built-in hook."""
        return ()

    def check_args(self, *args: str) -> Args:
        """Construct check-case-conflict arguments.

        Like `check-merge-conflict`, this tool has no autofix mode: two
        filenames differing only by case have no safe automatic rename,
        only a report.

        Args:
            *args: Additional arguments forwarded to `check-case-conflict`,
                typically the file paths to check.

        Returns:
            Args for `check-case-conflict`.
        """
        return Args(*args)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for checking for case-conflicting filenames.

        Left without a `types` restriction so it matches every file, like
        `check-added-large-files`: a case collision can occur between any
        two tracked paths regardless of content type. It runs after the
        general text-fixing chain.

        Returns:
            Hook metadata dict for `check-case-conflict`.
        """
        return VersionControlHookManager.I.builtin_hook(
            self.check_case_conflict,
            priority=VersionControlHookManager.I.deprioritize(
                EndOfFileFormatter.I.format_hook(),
            ),
        )

    def check_case_conflict(self) -> Args:
        """Return arguments for the built-in hook.

        Returns:
            Arguments passed to `check-case-conflict`.
        """
        return self.check_args()
