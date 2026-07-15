"""Wrapper around the rumdl Markdown linter tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.version_control.hook_manager import VersionControlHookManager


class MarkdownLinter(Tool):
    """Type-safe wrapper for the rumdl markdown linter.

    Constructs rumdl command-line arguments for linting and auto-fixing
    markdown files.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for rumdl."""
        return f"https://img.shields.io/badge/Markdown-{self.shield_name()}-darkgreen"

    def link_url(self) -> str:
        """Return the URL of the rumdl project page."""
        return "https://github.com/rvben/rumdl"

    def name(self) -> str:
        """Return `'rumdl'`, the executable name for this tool's CLI command."""
        return "rumdl"

    def version_control_ignore_patterns(self) -> tuple[str, ...]:
        """Return `('.rumdl_cache/',)`, rumdl's cache directory."""
        return (".rumdl_cache/",)

    def check_args(self, *args: str) -> Args:
        """Construct rumdl check arguments.

        Args:
            *args: Additional arguments forwarded to `rumdl check`.

        Returns:
            Args for `rumdl check`.
        """
        return self.args("check", *args)

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the Markdown linting hook.

        Returns:
            `check_markdown_hook`, wrapped in a single-element tuple.
        """
        return (self.check_markdown_hook(),)

    def check_markdown_hook(self) -> dict[str, Any]:
        """Return the hook metadata for linting and auto-fixing Markdown files.

        Runs after the sequential text-fixing chain, alongside the other
        file-type-specific fixers.

        Returns:
            Hook metadata dict for `rumdl check --fix`.
        """
        return VersionControlHookManager.I.hook(
            self.lint_markdown,
            priority=VersionControlHookManager.I.increase_priority(
                EndOfFileFormatter.I.format_end_of_file_hook(),
            ),
            types=["markdown"],
            args=["--fix"],
        )

    def lint_markdown(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `rumdl check`.
        """
        return self.check_args()
