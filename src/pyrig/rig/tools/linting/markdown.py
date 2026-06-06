"""Wrapper around the Markdown linter tool.

Wraps Markdown linter commands and information.
"""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup


class MarkdownLinter(Tool):
    """Type-safe wrapper for the rumdl markdown linter.

    Constructs rumdl command-line arguments for linting and auto-fixing
    markdown files.
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'rumdl'
        """
        return "rumdl"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            `ToolGroup.CODE_QUALITY`
        """
        return ToolGroup.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for rumdl.

        Returns:
            The URL of the badge image as a string.
        """
        return "https://img.shields.io/badge/markdown-rumdl-darkgreen"

    def link_url(self) -> str:
        """Return the link URL for rumdl.

        Returns:
            The URL of the rumdl project page as a string.
        """
        return "https://github.com/rvben/rumdl"

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return paths to ignore in version control."""
        return (".rumdl_cache/",)

    def check_fix_args(self, *args: str) -> Args:
        """Construct rumdl check arguments with auto-fix enabled.

        Args:
            *args: Additional arguments forwarded to ``rumdl check --fix``.

        Returns:
            Args for 'rumdl check --fix'.
        """
        return self.check_args("--fix", *args)

    def check_args(self, *args: str) -> Args:
        """Construct rumdl check arguments.

        Args:
            *args: Additional arguments forwarded to ``rumdl check``.

        Returns:
            Args for 'rumdl check'.
        """
        return self.args("check", *args)
