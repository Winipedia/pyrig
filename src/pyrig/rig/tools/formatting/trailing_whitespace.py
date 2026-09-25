"""Wrapper around the trailing-whitespace-fixer tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import FormatHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.formatting.end_of_line import EndOfLineFormatter
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class TrailingWhitespaceFormatter(FormatHookTool):
    """Type-safe wrapper for prek's pre-commit-hooks-compatible whitespace fixer."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for trailing-whitespace-fixer."""
        return f"https://img.shields.io/badge/whitespace-{self.shield_name()}-orange"

    def link_url(self) -> str:
        """Return the URL of the pre-commit-hooks project page."""
        return "https://github.com/pre-commit/pre-commit-hooks"

    def name(self) -> str:
        """Return `"trailing-whitespace-fixer"`, this tool's CLI command name."""
        return "trailing-whitespace-fixer"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return no package dependency; prek provides this built-in hook."""
        return ()

    def format_args(self, *args: str) -> Args:
        """Construct trailing-whitespace-fixer arguments.

        Unlike `pretty-format-json`, this tool has no separate autofix
        flag: it always rewrites a file's trailing whitespace in place and
        reports via its exit code whether anything changed.

        Args:
            *args: Additional arguments forwarded to
                `trailing-whitespace-fixer`, typically the file paths to fix.

        Returns:
            Args for `trailing-whitespace-fixer`.
        """
        return Args(*args)

    def format_hook(self) -> dict[str, Any]:
        """Return hook metadata for fixing trailing whitespace.

        Returns:
            Hook metadata dict for `trailing-whitespace-fixer`.
        """
        return VersionControlHookManager.I.builtin_hook(
            self.trailing_whitespace,
            priority=VersionControlHookManager.I.deprioritize(
                EndOfLineFormatter.I.format_hook(),
            ),
        )

    def trailing_whitespace(self) -> Args:
        """Return arguments for the built-in hook.

        Returns:
            Arguments passed to `trailing-whitespace-fixer`.
        """
        return self.format_args()
