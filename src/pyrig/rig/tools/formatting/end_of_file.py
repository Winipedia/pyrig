"""Wrapper around the end-of-file-fixer tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.formatting.trailing_whitespace import TrailingWhitespaceFormatter
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class EndOfFileFormatter(Tool):
    """Type-safe wrapper for the pre-commit-hooks end-of-file fixer."""

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
        """Return the package providing `end-of-file-fixer`."""
        return ("pre-commit-hooks",)

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
        return self.args(*args)

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the end-of-file hook.

        Returns:
            `format_end_of_file_hook`, wrapped in a single-element tuple.
        """
        return (self.format_end_of_file_hook(),)

    def format_end_of_file_hook(self) -> dict[str, Any]:
        """Return the hook metadata for fixing a file's trailing newline.

        Runs last among the sequential text-fixing hooks: it normalizes
        the very end of the file, a property no earlier fixer in the chain
        touches or could reintroduce a violation of.

        Returns:
            Hook metadata dict for `end-of-file-fixer`.
        """
        return VersionControlHookManager.I.hook(
            self.fix_end_of_file,
            priority=VersionControlHookManager.I.increase_priority(
                TrailingWhitespaceFormatter.I.format_trailing_whitespace_hook(),
            ),
            types=["text"],
        )

    def fix_end_of_file(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `end-of-file-fixer`.
        """
        return self.format_args()
