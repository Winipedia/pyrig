"""Pytest test runner wrapper.

Provides type-safe wrapper for pytest commands executed through UV (uv run pytest).
Ensures tests run in correct virtual environment.

Example:
    >>> from pyrig.dev.management.project_tester import ProjectTester
    >>> ProjectTester.L.get_run_tests_in_ci_args().run()
"""

from pyrig.dev.management.base.base import Tool
from pyrig.src.processes import Args


class ProjectTester(Tool):
    """Pytest test runner wrapper.

    Constructs pytest command arguments executed through UV.

    Operations:
        - Basic testing: Run pytest with custom arguments
        - CI testing: Run with CI flags (logging, coverage XML)

    Example:
        >>> ProjectTester.L.get_run_tests_in_ci_args().run()
        >>> ProjectTester.L.get_run_tests_in_ci_args("tests/test_module.py").run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'pytest'
        """
        return "pytest"

    @classmethod
    def get_coverage_threshold(cls) -> int:
        """Minimum test coverage percentage threshold."""
        return 90

    @classmethod
    def get_test_args(cls, *args: str) -> Args:
        """Construct uv run pytest arguments.

        Args:
            *args: Pytest command arguments.

        Returns:
            Args for 'uv run pytest'.
        """
        return cls.get_args(*args)

    @classmethod
    def get_run_tests_in_ci_args(cls, *args: str) -> Args:
        """Construct uv run pytest arguments for CI.

        Args:
            *args: Pytest command arguments.

        Returns:
            Args for 'uv run pytest' with CI flags (log level INFO, XML coverage).
        """
        return cls.get_test_args("--log-cli-level=INFO", "--cov-report=xml", *args)
