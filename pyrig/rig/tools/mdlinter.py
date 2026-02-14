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

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'rumdl'
        """
        return "rumdl"

    @classmethod
    def group(cls) -> str:
        """Get tool group.

        Returns:
            `ToolGroup.CODE_QUALITY`
        """
        return ToolGroup.CODE_QUALITY

    @classmethod
    def badge_urls(cls) -> tuple[str, str]:
        """Returns the badge and connected page."""
        return (
            "https://img.shields.io/badge/markdown-rumdl-darkgreen",
            "https://github.com/rvben/rumdl",
        )

    @classmethod
    def check_args(cls, *args: str) -> Args:
        """Construct rumdl check arguments.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'rumdl check'.
        """
        return cls.args("check", *args)

    @classmethod
    def check_fix_args(cls, *args: str) -> Args:
        """Construct rumdl check arguments with auto-fix.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'rumdl check --fix'.
        """
        return cls.check_args("--fix", *args)
