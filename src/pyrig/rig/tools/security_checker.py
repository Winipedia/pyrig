"""Bandit security checker wrapper.

Provides type-safe wrapper for Bandit commands.
Bandit is a tool designed to find common security issues in Python code.

Example:
    >>> from pyrig.rig.tools.security_checker import SecurityChecker
    >>> SecurityChecker.I.run_args("-r", ".").run()
    >>> SecurityChecker.I.run_with_config_args().run()
"""

from collections.abc import Generator
from pathlib import Path

from pyrig.core.processes import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester


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
            'bandit'
        """
        return "bandit"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            `ToolGroup.SECURITY`
        """
        return ToolGroup.SECURITY

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge image URL and project page URL."""
        return (
            "https://img.shields.io/badge/security-bandit-yellow.svg",
            "https://github.com/PyCQA/bandit",
        )

    def target_paths(self) -> tuple[Path, ...]:
        """Return target paths for security checking."""
        return (
            PackageManager.I.package_root(),
            ProjectTester.I.tests_package_root(),
        )

    def target_posix_paths(self) -> Generator[str, None, None]:
        """Return target paths as POSIX strings."""
        return (path.as_posix() for path in self.target_paths())

    def run_args(self, *args: str) -> Args:
        """Construct bandit arguments.

        Args:
            *args: Bandit command arguments.

        Returns:
            Args for 'bandit'.
        """
        return self.args(*args)

    def run_with_config_args(self, *args: str) -> Args:
        """Construct bandit arguments with pyproject.toml config.

        Args:
            *args: Bandit command arguments.

        Returns:
            Args for 'bandit -c pyproject.toml -r .'.
        """
        return self.run_args(
            "-c",
            "pyproject.toml",
            "-r",
            *self.target_posix_paths(),
            *args,
        )
