"""Wrapper around the end-of-file-fixer tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import FormatHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.formatting.trailing_whitespace import TrailingWhitespaceFormatter
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class EndOfFileFormatter(FormatHookTool):
    """Type-safe wrapper for prek's pre-commit-hooks-compatible EOF fixer."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for end-of-file-fixer."""
        return f"https://img.shields.io/badge/EOF-{self.shield_name()}-orange"

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"end-of-file-fixer"`, this tool's CLI command name."""
        return "end-of-file-fixer"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return no package dependency; prek provides this built-in hook."""
        return ()

    def format_args(self, *args: str) -> Args:
        """Construct end-of-file-fixer arguments.

        Like `trailing-whitespace-fixer`, this tool has no separate
        autofix flag: it always rewrites a file to end with exactly one
        trailing newline and reports via its exit code whether anything
        changed.

        Args:
            *args: Additional arguments forwarded to `end-of-file-fixer`,
                typically the file paths to fix.

        Returns:
            Args for `end-of-file-fixer`.
        """
        return Args(*args)

    def format_hook(self) -> dict[str, Any]:
        """Return hook metadata for fixing a file's trailing newline.

        Returns:
            Hook metadata dict for `end-of-file-fixer`.
        """
        return VersionControlHookManager.I.builtin_hook(
            self.end_of_file_fixer,
            priority=VersionControlHookManager.I.deprioritize(
                TrailingWhitespaceFormatter.I.format_hook(),
            ),
        )

    def end_of_file_fixer(self) -> Args:
        """Return arguments for the built-in hook.

        Returns:
            Arguments passed to `end-of-file-fixer`.
        """
        return self.format_args()
