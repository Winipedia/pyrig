"""Rumdl markdown linter wrapper.

Provides type-safe wrapper for rumdl commands: check, check --fix.
Rumdl is a fast markdown linter written in Rust.

Example:
    >>> from pyrig.rig.tools.mdlinter import MDLinter
    >>> MDLinter.I.check_args().run()
    >>> MDLinter.I.check_fix_args().run()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.src.processes import Args


class MDLinter(Tool):
    """Rumdl markdown linter wrapper.

    Constructs rumdl command arguments for markdown linting operations.

    Operations:
        - Linting: Check markdown files for issues
        - Auto-fix: Automatically fix markdown issues

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
        """Get tool group.

        Returns:
            `ToolGroup.CODE_QUALITY`
        """
        return ToolGroup.CODE_QUALITY

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge and link URLs."""
        return (
            "https://img.shields.io/badge/markdown-rumdl-darkgreen",
            "https://github.com/rvben/rumdl",
        )

    def check_args(self, *args: str) -> Args:
        """Construct rumdl check arguments.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'rumdl check'.
        """
        return self.args("check", *args)

    def check_fix_args(self, *args: str) -> Args:
        """Construct rumdl check arguments with auto-fix.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'rumdl check --fix'.
        """
        return self.check_args("--fix", *args)
