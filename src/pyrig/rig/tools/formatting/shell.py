"""Wrapper around the shfmt shell script formatter tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import FormatHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class ShellFormatter(FormatHookTool):
    """A formatter for shell commands."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for shfmt."""
        return f"https://img.shields.io/badge/shell-{self.shield_name()}-orange"

    def link_url(self) -> str:
        """Return the URL of the shfmt project page."""
        return "https://github.com/mvdan/sh"

    def name(self) -> str:
        """Return `'shfmt'`, the executable name for this tool's CLI command."""
        return "shfmt"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return `('shfmt-py',)`, the PyPI package providing `shfmt`."""
        return ("shfmt-py",)

    def format_args(self, *args: str) -> Args:
        """Construct shfmt formatting arguments at maximum strictness.

        Uses 2-space indentation, matching the Google Shell Style Guide
        (https://google.github.io/styleguide/shellguide.html), the most
        widely adopted shell formatting convention. Also indents `case`
        statement bodies, pins the dialect to `bash` rather than relying on
        shebang detection, and writes changes back to each file rather than
        only reporting a diff.

        Args:
            *args: Additional arguments forwarded to `shfmt`, typically the
                file paths to format.

        Returns:
            Args for `shfmt --indent=2 --case-indent --language-dialect=bash --write`.
        """
        return self.args(*args)

    def format_hook(self) -> dict[str, Any]:
        """Return the hook metadata for formatting shell scripts.

        Runs after the sequential text-fixing chain, alongside the other
        file-type-specific fixers.

        Returns:
            Hook metadata dict for `shfmt`.
        """
        return VersionControlHookManager.I.hook(
            self.format_shell,
            priority=VersionControlHookManager.I.increase_priority(
                EndOfFileFormatter.I.format_hook(),
            ),
            types=["shell"],
            args=[
                "--indent=2",
                "--case-indent",
                "--language-dialect=bash",
                "--write",
            ],
        )

    def format_shell(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run shfmt`.
        """
        return PackageManager.I.run_args(*self.format_args())
