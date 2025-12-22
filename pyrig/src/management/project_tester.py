"""Tests runner utilities.

This module provides utilities for running tests.
"""

from pyrig.src.management.base.base import Args, Tool
from pyrig.src.management.package_manager import PackageManager


class ProjectTester(Tool):
    """Pytest test runner tool.

    Provides methods for constructing pytest command arguments through uv run.
    """

    @classmethod
    def name(cls) -> str:
        """Get the tool name.

        Returns:
            str: The string 'pytest'.
        """
        return "pytest"

    @classmethod
    def get_run_tests_args(cls, *args: str) -> Args:
        """Construct uv run pytest command arguments.

        Args:
            *args: Additional arguments to append to the pytest command.

        Returns:
            Args: Command arguments for 'uv run pytest'.
        """
        return PackageManager.get_run_args(cls.name(), *args)

    @classmethod
    def get_run_tests_in_ci_args(cls, *args: str) -> Args:
        """Construct uv run pytest command arguments for CI environment.

        Args:
            *args: Additional arguments to append to the pytest command.

        Returns:
            Args: Command arguments for 'uv run pytest' with CI-specific flags
                including log level INFO and XML coverage report.
        """
        return cls.get_run_tests_args("--log-cli-level=INFO", "--cov-report=xml", *args)
