"""Wrapper around the rumdl Markdown linter tool."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group


class MarkdownLinter(FileTool):
    """Type-safe wrapper for the rumdl markdown linter.

    Constructs rumdl command-line arguments for linting and auto-fixing
    markdown files.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`, the badge group this tool belongs to."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for rumdl."""
        return "https://img.shields.io/badge/markdown-rumdl-darkgreen"

    def link_url(self) -> str:
        """Return the URL of the rumdl project page."""
        return "https://github.com/rvben/rumdl"

    def name(self) -> str:
        """Return `'rumdl'`, the executable name for this tool's CLI command."""
        return "rumdl"

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return `('.rumdl_cache/',)`, rumdl's cache directory."""
        return (".rumdl_cache/",)

    def types(self) -> list[str]:
        """Return the list of file types that `rumdl` can lint."""
        return ["markdown"]

    def check_fix_args(self, *args: str) -> Args:
        """Construct rumdl check arguments with auto-fix enabled.

        Args:
            *args: Additional arguments forwarded to `rumdl check --fix`.

        Returns:
            Args for `rumdl check --fix`.
        """
        return self.check_args("--fix", *args)

    def check_args(self, *args: str) -> Args:
        """Construct rumdl check arguments.

        Args:
            *args: Additional arguments forwarded to `rumdl check`.

        Returns:
            Args for `rumdl check`.
        """
        return self.args("check", *args)
