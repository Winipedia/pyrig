"""Wrapper around the check-added-large-files tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import CheckHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class LargeFileChecker(CheckHookTool):
    """Type-safe wrapper for the pre-commit-hooks large file checker."""

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
        """Return the package providing `check-added-large-files`."""
        return ("pre-commit-hooks",)

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
        return self.args(*args)

    def check_hook(self) -> dict[str, Any]:
        """Return the hook metadata for checking for accidentally added large files.

        Left without a `types` restriction so it matches every file,
        binary included, since a large binary is exactly what this check
        exists to catch. Ties its priority to `TypeChecker.check_hook`
        so it runs alongside the rest of the checks tier rather than after
        it.

        Returns:
            Hook metadata dict for `check-added-large-files`.
        """
        return VersionControlHookManager.I.hook(
            self.check_large_files,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_hook(),
            ),
        )

    def check_large_files(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `check-added-large-files`.
        """
        return self.check_args()
