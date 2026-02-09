"""Rumdl markdown linter wrapper.

Provides type-safe wrapper for rumdl commands: check.
Rumdl is a fast markdown linter written in Rust.

Example:
    >>> from pyrig.dev.management.mdlinter import MDLinter
    >>> MDLinter.L.get_check_args().run()
    >>> MDLinter.L.get_check_fix_args().run()
"""

from pyrig.dev.management.base.base import Tool
from pyrig.src.processes import Args


class MDLinter(Tool):
    """Rumdl markdown linter wrapper.

    Constructs rumdl command arguments for markdown linting operations.

    Operations:
        - Linting: Check markdown files for issues
        - Auto-fix: Automatically fix markdown issues

    Example:
        >>> MDLinter.L.get_check_args().run()
        >>> MDLinter.L.get_check_fix_args().run()
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
        """Construct rumdl check arguments with auto-fix.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'rumdl check --fix'.
        """
        return cls.get_check_args("--fix", *args)

    @classmethod
    def get_ignore_too_long_line_start(cls) -> str:
        """Get the rumdl argument to ignore too long line.

        This should start the region where to ignore it.

        Returns:
            str: '--ignore MD013'
        """
        return "<!-- rumdl-disable MD013 -->"

    @classmethod
    def get_ignore_too_long_line_end(cls) -> str:
        """Get the rumdl argument to ignore too long line.

        This should end the region where to ignore it.

        Returns:
            str: '--ignore MD013'
        """
        return "<!-- rumdl-enable MD013 -->"
