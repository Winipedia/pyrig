"""Rumdl markdown linter wrapper.

Provides type-safe wrapper for rumdl commands: check, fix.
Rumdl is a fast markdown linter written in Rust.

Example:
    >>> from pyrig.src.management.mdlinter import MDLinter
    >>> MDLinter.get_check_args().run()
    >>> MDLinter.get_fix_args().run()
"""

from pyrig.src.management.base.base import Tool
from pyrig.src.processes import Args


class MDLinter(Tool):
    """Rumdl markdown linter wrapper.

    Constructs rumdl command arguments for markdown linting operations.

    Operations:
        - Linting: Check markdown files for issues
        - Auto-fix: Automatically fix markdown issues

    Example:
        >>> MDLinter.get_check_args().run()
        >>> MDLinter.get_fix_args().run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'rumdl'
        """
        return "rumdl"

    @classmethod
    def get_check_args(cls, *args: str) -> Args:
        """Construct rumdl check arguments.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'rumdl check'.
        """
        return cls.get_args("check", *args)

    @classmethod
    def get_check_fix_args(cls, *args: str) -> Args:
        """Construct rumdl fix arguments.

        Args:
            *args: Fix command arguments.

        Returns:
            Args for 'rumdl fix'.
        """
        return cls.get_check_args("--fix", *args)
