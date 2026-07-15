"""Wrapper around the trailing-whitespace-fixer tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.spelling.checker import SpellChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class TrailingWhitespaceFormatter(Tool):
    """Type-safe wrapper for the pre-commit-hooks trailing whitespace fixer."""

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
        """Return the package providing `trailing-whitespace-fixer`."""
        return ("pre-commit-hooks",)

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
        return self.args(*args)

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the trailing whitespace hook.

        Returns:
            `format_trailing_whitespace_hook`, wrapped in a single-element
            tuple.
        """
        return (self.format_trailing_whitespace_hook(),)

    def format_trailing_whitespace_hook(self) -> dict[str, Any]:
        """Return the hook metadata for fixing trailing whitespace.

        Runs after spelling is fixed, so a spelling correction never
        reintroduces trailing whitespace this hook already cleaned up.

        Returns:
            Hook metadata dict for `trailing-whitespace-fixer`.
        """
        return VersionControlHookManager.I.hook(
            self.fix_trailing_whitespace,
            priority=VersionControlHookManager.I.increase_priority(
                SpellChecker.I.check_spelling_hook(),
            ),
            types=["text"],
        )

    def fix_trailing_whitespace(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `trailing-whitespace-fixer`.
        """
        return self.format_args()
