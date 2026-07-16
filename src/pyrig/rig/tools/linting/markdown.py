"""Wrapper around the rumdl Markdown linter tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class MarkdownLinter(Tool):
    """Type-safe wrapper for the rumdl markdown linter.

    Constructs rumdl command-line arguments for linting and, separately,
    formatting markdown files.
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

    def lint_args(self, *args: str) -> Args:
        """Construct rumdl check arguments.

        Args:
            *args: Additional arguments forwarded to `rumdl check`.

        Returns:
            Args for `rumdl check`.
        """
        return self.args("check", *args)

    def format_args(self, *args: str) -> Args:
        """Construct rumdl fmt arguments.

        Args:
            *args: Additional arguments forwarded to `rumdl fmt`.

        Returns:
            Args for `rumdl fmt`.
        """
        return self.args("fmt", *args)

    def version_control_hooks(self) -> tuple[dict[str, Any], ...]:
        """Return the Markdown linting and formatting hooks.

        Returns:
            `lint_hook` and `format_hook`, in that order.
        """
        return (self.lint_hook(), self.format_hook())

    def lint_hook(self) -> dict[str, Any]:
        """Return the hook metadata for linting Markdown files.

        Ties its priority to `TypeChecker.check_hook` so it runs
        alongside the rest of the checks tier rather than after it.

        Returns:
            Hook metadata dict for `rumdl check`.
        """
        return VersionControlHookManager.I.hook(
            self.lint_markdown,
            priority=VersionControlHookManager.I.hook_priority(
                TypeChecker.I.check_hook(),
            ),
            types=["markdown"],
        )

    def lint_markdown(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `rumdl check`.
        """
        return self.lint_args()

    def format_hook(self) -> dict[str, Any]:
        """Return the hook metadata for formatting Markdown files.

        Runs after the sequential text-fixing chain, alongside the other
        file-type-specific fixers.

        Returns:
            Hook metadata dict for `rumdl fmt`.
        """
        return VersionControlHookManager.I.hook(
            self.format_markdown,
            priority=VersionControlHookManager.I.increase_priority(
                EndOfFileFormatter.I.format_hook(),
            ),
            types=["markdown"],
        )

    def format_markdown(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `rumdl fmt`.
        """
        return self.format_args()
