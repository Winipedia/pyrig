"""Pytest test runner wrapper.

Provides type-safe wrapper for pytest command argument construction.

Example:
    >>> from pyrig.rig.tools.project_tester import ProjectTester
    >>> ProjectTester.I.run_tests_in_ci_args().run()
"""

import os
from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup
from pyrig.rig.tools.project_coverage_tester import ProjectCoverageTester


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
            'pytest'
        """
        return "pytest"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            `ToolGroup.TESTING`
        """
        return ToolGroup.TESTING

    def badge_urls(self) -> tuple[str, str]:
        """Get pytest badge image URL and project page URL."""
        return (
            "https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest",
            "https://pytest.org",
        )

    def dev_dependencies(self) -> tuple[str, ...]:
        """Get tool dependencies.

        Returns:
            Tuple of tool dependencies.
        """
        return (*super().dev_dependencies(), "pytest-mock")

    def tests_package_name(self) -> str:
        """Get tests package name.

        Returns:
            The ``"tests"`` package name string.
        """
        return "tests"

    def test_module_prefix(self) -> str:
        """Get test module filename prefix.

        Returns:
            The test module filename prefix string (e.g., "test_").
        """
        return "test_"

    def tests_source_root(self) -> Path:
        """Get tests source root directory path."""
        return Path()

    def tests_package_root(self) -> Path:
        """Get tests package root directory path.

        Returns:
            Path to the tests package root directory (e.g., ``Path("tests")``).
        """
        return self.tests_source_root() / self.tests_package_name()

    def is_running_tests(self) -> bool:
        """Determine if tests are currently running.

        Returns:
            True if tests are running, False otherwise.
        """
        return os.getenv("PYTEST_VERSION") is not None

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
        return self.test_args(
            "--log-cli-level=INFO", *ProjectCoverageTester.I.additional_ci_args(), *args
        )
