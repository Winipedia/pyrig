"""Bandit security checker wrapper.

Provides type-safe wrapper for Bandit commands.
Bandit is a tool designed to find common security issues in Python code.

Example:
    >>> from pyrig.rig.tools.security_checker import SecurityChecker
    >>> SecurityChecker.L.get_run_args("-r", ".").run()
    >>> SecurityChecker.L.get_run_with_config_args().run()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.src.processes import Args


class SecurityChecker(Tool):
    """Bandit security checker wrapper.

    Constructs bandit command arguments for security checking operations.

    Operations:
        - Security scanning: Find common security issues in Python code
        - Recursive scanning: Scan directories recursively
        - Config-based scanning: Use pyproject.toml configuration

    Example:
        >>> SecurityChecker.L.get_run_args("-r", ".").run()
        >>> SecurityChecker.L.get_run_with_config_args().run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'bandit'
        """
        return "bandit"

    @classmethod
    def group(cls) -> str:
        """Returns the group the tools belongs to.

        E.g. testing, tool, code-quality etc...
        """
        return ToolGroup.SECURITY

    @classmethod
    def badge_urls(cls) -> tuple[str, str]:
        """Returns the badge and connected page."""
        return (
            "https://img.shields.io/badge/security-bandit-yellow.svg",
            "https://github.com/PyCQA/bandit",
        )

    @classmethod
    def get_run_args(cls, *args: str) -> Args:
        """Construct bandit arguments.

        Args:
            *args: Bandit command arguments.

        Returns:
            Args for 'bandit'.
        """
        return cls.build_args(*args)

    @classmethod
    def get_run_with_config_args(cls, *args: str) -> Args:
        """Construct bandit arguments with pyproject.toml config.

        Args:
            *args: Bandit command arguments.

        Returns:
            Args for 'bandit -c pyproject.toml -r .'.
        """
        return cls.get_run_args("-c", "pyproject.toml", "-r", ".", *args)
