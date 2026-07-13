"""Wrapper around the shfmt shell script formatter tool."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.linting.shell import ShellLinter


class ShellFormatter(FileTool):
    """A formatter for shell commands."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for shfmt."""
        return "https://img.shields.io/badge/shell-shfmt-orange"

    def link_url(self) -> str:
        """Return the URL of the shfmt project page."""
        return "https://github.com/mvdan/sh"

    def name(self) -> str:
        """Return `'shfmt'`, the executable name for this tool's CLI command."""
        return "shfmt"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return `('shfmt-py',)`, the PyPI package providing `shfmt`."""
        return ("shfmt-py",)

    def types(self) -> list[str]:
        """Return the list of file types that `shfmt` can format."""
        return ShellLinter.I.types()

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
            Args for `shfmt -i 2 -ci -ln bash -w`.
        """
        return self.args(
            "-i",
            "2",
            "-ci",
            "-ln",
            "bash",
            "-w",
            *args,
        )
