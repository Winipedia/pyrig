"""Pytest test runner wrapper.

Provides type-safe wrapper for pytest command argument construction.

Example:
    >>> from pyrig.rig.tools.project_tester import ProjectTester
    >>> ProjectTester.I.run_tests_in_ci_args().run()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.src.processes import Args


class ProjectTester(Tool):
    """Pytest test runner wrapper.

    Constructs pytest command arguments.

    Operations:
        - Basic testing: Run pytest with custom arguments
        - CI testing: Run with CI flags (logging, coverage XML)

    Example:
        >>> ProjectTester.I.run_tests_in_ci_args().run()
        >>> ProjectTester.I.run_tests_in_ci_args("tests/test_module.py").run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'pytest'
        """
        return "pytest"

    @classmethod
    def group(cls) -> str:
        """Get badge group.

        Returns:
            `ToolGroup.TESTING`
        """
        return ToolGroup.TESTING

    @classmethod
    def badge_urls(cls) -> tuple[str, str]:
        """Get pytest badge image URL and project page URL."""
        return (
            "https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest",
            "https://pytest.org",
        )

    @classmethod
    def dev_dependencies(cls) -> list[str]:
        """Get tool dependencies.

        Returns:
            List of tool dependencies.
        """
        return [*super().dev_dependencies(), "pytest-mock"]

    @classmethod
    def coverage_threshold(cls) -> int:
        """Get minimum test coverage percentage threshold.

        Returns:
            Coverage percentage (90).
        """
        return 90

    @classmethod
    def test_args(cls, *args: str) -> Args:
        """Construct pytest arguments.

        Args:
            *args: Pytest command arguments.

        Returns:
            Args for 'pytest'.
        """
        return cls.args(*args)

    @classmethod
    def run_tests_in_ci_args(cls, *args: str) -> Args:
        """Construct pytest arguments for CI.

        Args:
            *args: Pytest command arguments.

        Returns:
            Args for 'pytest' with CI flags (log level INFO, XML coverage).
        """
        return cls.test_args("--log-cli-level=INFO", "--cov-report=xml", *args)
