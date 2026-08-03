"""Wrapper around the shfmt shell script formatter tool."""

from typing import Any

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.hooks import FormatHookTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.linting.shell import ShellLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class ShellFormatter(FormatHookTool):
    """Type-safe wrapper for the shfmt shell script formatter."""

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
        """Construct shfmt arguments.

        Unlike `trailing-whitespace-fixer`, `shfmt` needs an explicit
        `--write` flag to write changes back instead of printing the
        formatted result to stdout.

        Args:
            *args: Additional arguments forwarded to `shfmt`, typically the
                file paths to format.

        Returns:
            Args for `shfmt`.
        """
        return self.args(*args)

    def format_hook(self) -> dict[str, Any]:
        """Return the hook metadata for formatting shell scripts.

        Runs after the sequential text-fixing chain, alongside the other
        file-type-specific fixers. Passes `--write` so changes are written
        back to each file rather than only printed to stdout. Uses 2-space
        indentation and puts a wrapped pipeline's `|`, `&&`, or `||` at the
        start of the continuation line rather than the end of the previous
        one, matching the Google Shell Style Guide
        (https://google.github.io/styleguide/shellguide.html), the most
        widely adopted shell formatting convention. Also indents `case`
        statement bodies, pins the dialect rather than relying on shebang
        detection, and simplifies redundant syntax (e.g. useless
        parentheses, duplicate subshells, and superfluous quoting).

        Returns:
            Hook metadata dict for `shfmt` with `--indent=2 --case-indent
            --language-dialect=bash --simplify --binary-next-line --write`.
        """
        return VersionControlHookManager.I.hook(
            self.format_shell,
            priority=VersionControlHookManager.I.increase_priority(
                EndOfFileFormatter.I.format_hook(),
            ),
            types=["shell"],
            args=[
                "--binary-next-line",
                "--case-indent",
                "--indent=2",
                f"--language-dialect={ShellLinter.I.dialect()}",
                "--simplify",
                "--write",
            ],
        )

    def format_shell(self) -> Args:
        """Return the `Args` this hook's entry runs.

        Returns:
            Args for `uv run shfmt`.
        """
        return PackageManager.I.run_args(*self.format_args())
