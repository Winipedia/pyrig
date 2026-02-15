"""Bandit security checker wrapper.

Provides type-safe wrapper for Bandit commands.
Bandit is a tool designed to find common security issues in Python code.

Example:
    >>> from pyrig.rig.tools.security_checker import SecurityChecker
    >>> SecurityChecker.I.run_args("-r", ".").run()
    >>> SecurityChecker.I.run_with_config_args().run()
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
        >>> SecurityChecker.I.run_args("-r", ".").run()
        >>> SecurityChecker.I.run_with_config_args().run()
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            str: The tool name 'bandit'.
        """
        return "bandit"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            str: The tool group ToolGroup.SECURITY.
        """
        return ToolGroup.SECURITY

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge image URL and project page URL.

        Returns:
            tuple[str, str]: A tuple containing the badge image URL and project page URL.
        """
        return (
            "https://img.shields.io/badge/security-bandit-yellow.svg",
            "https://github.com/PyCQA/bandit",
        )

    def run_args(self, *args: str) -> Args:
        """Construct bandit arguments.

        Args:
            *args: Bandit command arguments.

        Returns:
            Args: Args object for 'bandit' command.
        """
        return self.args(*args)

    def run_with_config_args(self, *args: str) -> Args:
        """Construct bandit arguments with pyproject.toml config.

        Args:
            *args: Bandit command arguments.

        Returns:
            Args: Args object for 'bandit -c pyproject.toml -r .' command.
        """
        return self.run_args("-c", "pyproject.toml", "-r", ".", *args)
