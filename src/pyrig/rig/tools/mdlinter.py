"""Markdown linter tool wrapper.

Wraps the rumdl command-line tool with a type-safe interface for
constructing markdown linting arguments. Rumdl is a fast markdown
linter written in Rust.

Example:
    >>> from pyrig.rig.tools.mdlinter import MDLinter
    >>> MDLinter.I.check_args().run()
    >>> MDLinter.I.check_fix_args().run()
"""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup


class MDLinter(Tool):
    """Type-safe wrapper for the rumdl markdown linter.

    Constructs rumdl command-line arguments for linting and auto-fixing
    markdown files.

    Example:
        >>> MDLinter.I.check_args().run()
        >>> MDLinter.I.check_fix_args().run()
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

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge and link URLs for rumdl.

        Returns:
            A tuple of ``(badge_url, link_url)`` where ``badge_url`` is the
            shield image URL and ``link_url`` is the rumdl project page.
        """
        return (
            "https://img.shields.io/badge/markdown-rumdl-darkgreen",
            "https://github.com/rvben/rumdl",
        )

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
