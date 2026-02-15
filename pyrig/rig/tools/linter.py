"""Ruff linter and formatter wrapper.

Provides type-safe wrapper for Ruff commands: check, check --fix, format.
Ruff is a fast Python linter and formatter written in Rust.

Example:
    >>> from pyrig.rig.tools.linter import Linter
    >>> Linter.I.check_args().run()
    >>> Linter.I.check_fix_args().run()
    >>> Linter.I.format_args().run()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.src.processes import Args


class Linter(Tool):
    """Ruff linter and formatter wrapper.

    Constructs ruff command arguments for linting and formatting operations.

    Operations:
        - Linting: Check code for issues
        - Formatting: Format code to style guidelines
        - Auto-fix: Automatically fix linting issues

    Example:
        >>> Linter.I.check_args().run()
        >>> Linter.I.check_fix_args().run()
        >>> Linter.I.format_args().run()
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'ruff'
        """
        return "ruff"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            `ToolGroup.CODE_QUALITY`
        """
        return ToolGroup.CODE_QUALITY

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge and link URLs."""
        return (
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json",
            "https://github.com/astral-sh/ruff",
        )

    def check_args(self, *args: str) -> Args:
        """Construct ruff check arguments.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'ruff check'.
        """
        return self.args("check", *args)

    def check_fix_args(self, *args: str) -> Args:
        """Construct ruff check arguments with auto-fix.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'ruff check --fix'.
        """
        return self.check_args("--fix", *args)

    def format_args(self, *args: str) -> Args:
        """Construct ruff format arguments.

        Args:
            *args: Format command arguments.

        Returns:
            Args for 'ruff format'.
        """
        return self.args("format", *args)
