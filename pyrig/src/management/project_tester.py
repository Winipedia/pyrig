"""Pytest test runner wrapper for executing project tests.

This module provides a type-safe wrapper for pytest test execution commands.
The `ProjectTester` class constructs pytest command arguments that are run
through UV's environment management (uv run pytest).

Pytest is pyrig's test framework of choice, providing powerful test discovery,
fixtures, and reporting capabilities.

Example:
    >>> from pyrig.src.management.project_tester import ProjectTester
    >>> # Run all tests
    >>> test_args = ProjectTester.get_run_tests_args()
    >>> print(test_args)
    uv run pytest
    >>> test_args.run()
    >>>
    >>> # Run tests with coverage in CI
    >>> ci_args = ProjectTester.get_run_tests_in_ci_args()
    >>> ci_args.run()

See Also:
    pyrig.src.management.base.base.Tool: Base class for tool wrappers
    pyrig.src.management.package_manager.PackageManager: UV wrapper
    pyrig.dev.cli.subcommands.test: CLI test command
"""

from pyrig.src.management.base.base import Args, Tool
from pyrig.src.management.package_manager import PackageManager


class ProjectTester(Tool):
    """Pytest test runner tool wrapper.

    Provides methods for constructing pytest command arguments that are executed
    through UV's environment management. This ensures tests run in the correct
    virtual environment with all dependencies available.

    The class provides methods for:
        - **Basic testing**: Run pytest with custom arguments
        - **CI testing**: Run with CI-specific flags (logging, coverage XML)

    All methods return `Args` objects that can be executed via `.run()` or
    converted to strings for display.

    Example:
        >>> # Run specific test file
        >>> ProjectTester.get_run_tests_args("tests/test_module.py").run()
        >>>
        >>> # Run with coverage
        >>> ProjectTester.get_run_tests_args("--cov=mypackage").run()

    See Also:
        pyrig.src.management.base.base.Tool: Base class
        pyrig.src.management.package_manager.PackageManager: UV wrapper
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
