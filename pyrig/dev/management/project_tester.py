"""Pytest test runner wrapper.

Provides type-safe wrapper for pytest commands executed through UV (uv run pytest).
Ensures tests run in correct virtual environment.

Example:
    >>> from pyrig.src.management.project_tester import ProjectTester
    >>> ProjectTester.get_run_tests_args().run()
    >>> ProjectTester.get_run_tests_in_ci_args().run()
"""

from pyrig.dev.management.base.base import Tool
from pyrig.dev.management.package_manager import PackageManager
from pyrig.src.processes import Args


class ProjectTester(Tool):
    """Pytest test runner wrapper.

    Constructs pytest command arguments executed through UV.

    Operations:
        - Basic testing: Run pytest with custom arguments
        - CI testing: Run with CI flags (logging, coverage XML)

    Example:
        >>> ProjectTester.get_run_tests_args("tests/test_module.py").run()
        >>> ProjectTester.get_run_tests_args("--cov=mypackage").run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'pytest'
        """
        return "pytest"

    @classmethod
    def get_run_tests_args(cls, *args: str) -> Args:
        """Construct uv run pytest arguments.

        Args:
            *args: Pytest command arguments.

        Returns:
            Args for 'uv run pytest'.
        """
        return PackageManager.get_run_args(cls.name(), *args)

    @classmethod
    def get_run_tests_in_ci_args(cls, *args: str) -> Args:
        """Construct uv run pytest arguments for CI.

        Args:
            *args: Pytest command arguments.

        Returns:
            Args for 'uv run pytest' with CI flags (log level INFO, XML coverage).
        """
        return cls.get_run_tests_args("--log-cli-level=INFO", "--cov-report=xml", *args)
