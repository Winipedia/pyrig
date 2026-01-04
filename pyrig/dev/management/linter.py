"""Ruff linter and formatter wrapper.

Provides type-safe wrapper for Ruff commands: check, format.
Ruff is a fast Python linter and formatter written in Rust.

Example:
    >>> from pyrig.dev.management.linter import Linter
    >>> Linter.L.get_check_args().run()
    >>> Linter.L.get_format_args().run()
"""

from pyrig.dev.management.base.base import Tool
from pyrig.src.processes import Args


class Linter(Tool):
    """Ruff linter and formatter wrapper.

    Constructs ruff command arguments for linting and formatting operations.

    Operations:
        - Linting: Check code for issues
        - Formatting: Format code to style guidelines
        - Auto-fix: Automatically fix linting issues

    Example:
        >>> Linter.L.get_check_args().run()
        >>> Linter.L.get_check_fix_args().run()
        >>> Linter.L.get_format_args().run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'ruff'
        """
        return "ruff"

    @classmethod
    def get_check_args(cls, *args: str) -> Args:
        """Construct ruff check arguments.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'ruff check'.
        """
        return cls.get_args("check", *args)

    @classmethod
    def get_check_fix_args(cls, *args: str) -> Args:
        """Construct ruff check arguments with auto-fix.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'ruff check --fix'.
        """
        return cls.get_check_args("--fix", *args)

    @classmethod
    def get_format_args(cls, *args: str) -> Args:
        """Construct ruff format arguments.

        Args:
            *args: Format command arguments.

        Returns:
            Args for 'ruff format'.
        """
        return cls.get_args("format", *args)
