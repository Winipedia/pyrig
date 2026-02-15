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

    def name(self) -> str:
        """Get tool name.

        Returns:
            The name of the pytest tool.
        """
        return "pytest"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            The testing tool group.
        """
        return ToolGroup.TESTING

    def badge_urls(self) -> tuple[str, str]:
        """Get pytest badge image URL and project page URL.

        Returns:
            A tuple of badge image URL and project page URL.
        """
        return (
            "https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest",
            "https://pytest.org",
        )

    def dev_dependencies(self) -> list[str]:
        """Get tool dependencies.

        Returns:
            List of tool dependencies.
        """
        return [*super().dev_dependencies(), "pytest-mock"]

    def coverage_threshold(self) -> int:
        """Get minimum test coverage percentage threshold.

        Returns:
            Minimum coverage percentage threshold.
        """
        return 90

    def test_args(self, *args: str) -> Args:
        """Construct pytest arguments.

        Args:
            *args: Pytest command arguments.

        Returns:
            Args for 'pytest'.
        """
        return self.args(*args)

    def run_tests_in_ci_args(self, *args: str) -> Args:
        """Construct pytest arguments for CI.

        Args:
            *args: Pytest command arguments.

        Returns:
            Args for 'pytest' with CI flags (log level INFO, XML coverage).
        """
        return self.test_args("--log-cli-level=INFO", "--cov-report=xml", *args)
