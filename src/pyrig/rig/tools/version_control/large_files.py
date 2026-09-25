"""Wrapper around the check-added-large-files tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class LargeFileChecker(CheckHookTool):
    """Type-safe wrapper for prek's pre-commit-hooks-compatible large file check."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for check-added-large-files."""
        return f"https://img.shields.io/badge/large--files-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"check-added-large-files"`, this tool's CLI command name."""
        return "check-added-large-files"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return no package dependency; prek provides this built-in hook."""
        return ()

    def check_args(self, *args: str) -> Args:
        """Construct check-added-large-files arguments.

        Like `check-merge-conflict`, this tool has no autofix mode: an
        oversized file has no safe automatic remedy, only a report.

        Args:
            *args: Additional arguments forwarded to
                `check-added-large-files`, typically the file paths to check.

        Returns:
            Args for `check-added-large-files`.
        """
        return Args("--enforce-all", *args)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for checking for accidentally added large files.

        Left without a `types` restriction so it matches every file,
        binary included, since a large binary is exactly what this check
        exists to catch.
        Runs after the general text-fixing chain.

        Returns:
            Hook metadata dict for `check-added-large-files --enforce-all`.
        """
        return VersionControlHookManager.I.builtin_hook(
            self.check_added_large_files,
            priority=VersionControlHookManager.I.deprioritize(
                EndOfFileFormatter.I.format_hook(),
            ),
        )

    def check_added_large_files(self) -> Args:
        """Return arguments for the built-in hook.

        Returns:
            Arguments passed to `check-added-large-files`.
        """
        return self.check_args()
