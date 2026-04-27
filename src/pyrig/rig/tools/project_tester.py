"""Project tester wrapper.

Wraps ProjectTester commands and information.
"""

from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup
from pyrig.rig.tools.project_coverage_tester import ProjectCoverageTester


class ProjectTester(Tool):
    """Pytest runner and test-layout configuration.

    Centralizes test-related constants (package name, source root, module
    prefix) used throughout the project for path resolution, config
    generation, and mirror-test discovery. Also constructs pytest command
    argument tuples for both local and CI execution.

    Example:
        >>> ProjectTester.I.run_tests_in_ci_args().run()
        >>> ProjectTester.I.run_tests_in_ci_args("tests/test_module.py").run()
    """

    def name(self) -> str:
        """Get the pytest command name.

        Returns:
            'pytest'
        """
        return "pytest"

    def group(self) -> str:
        """Get the badge group for this tool.

        Returns:
            'testing'
        """
        return ToolGroup.TESTING

    def badge_urls(self) -> tuple[str, str]:
        """Get the pytest badge image URL and the pytest project page URL.

        Returns:
            Tuple of ``(badge_image_url, project_page_url)``.
        """
        return (
            "https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest",
            "https://pytest.org",
        )

    def dev_dependencies(self) -> tuple[str, ...]:
        """Get the dev dependencies required by this tool.

        Extends the base dependency (``pytest``) with ``pytest-mock``.

        Returns:
            ``('pytest', 'pytest-mock')``
        """
        return (*super().dev_dependencies(), "pytest-mock")

    def tests_package_root(self) -> Path:
        """Get the root directory of the tests package.

        Derived from :meth:`tests_source_root` and :meth:`tests_package_name`.

        Returns:
            Path to the tests package root (e.g., ``Path("tests")``).
        """
        return self.tests_source_root() / self.tests_package_name()

    def tests_source_root(self) -> Path:
        """Get the source root that contains the tests package.

        Returns ``Path()``, an empty path representing the project root.
        This means the ``tests/`` package lives directly at the project
        root rather than under a ``src/`` subdirectory.

        Returns:
            ``Path()`` (the project root directory).
        """
        return Path()

    def tests_package_name(self) -> str:
        """Get the name of the top-level tests package.

        This value is used project-wide to locate test packages, resolve
        module paths, and distinguish test files from source files in
        config generation and mirror-test discovery.

        Returns:
            ``'tests'``
        """
        return "tests"

    def test_module_prefix(self) -> str:
        """Get the filename prefix for test modules.

        All test module filenames must start with this prefix. Used in
        config generation (e.g., ruff per-file ignores) and mirror-test
        discovery to identify and construct test module names.

        Returns:
            ``'test_'``
        """
        return "test_"

    def run_tests_in_ci_args(self, *args: str) -> Args:
        """Construct pytest arguments for CI execution.

        Prepends ``--log-cli-level=INFO`` for live log output followed by
        coverage XML reporting args from
        :meth:`~pyrig.rig.tools.project_coverage_tester.ProjectCoverageTester.additional_ci_args`.
        The resulting command is used in CI workflow steps (e.g., the
        build workflow's test step).

        Args:
            *args: Additional pytest arguments to append.

        Returns:
            Args for ``pytest`` with CI flags prepended.
        """
        return self.test_args(
            "--log-cli-level=INFO", *ProjectCoverageTester.I.additional_ci_args(), *args
        )

    def test_args(self, *args: str) -> Args:
        """Construct pytest command arguments.

        Prepends the ``pytest`` command name to the given arguments.

        Args:
            *args: Pytest command arguments to pass after the command name.

        Returns:
            Args starting with ``'pytest'`` followed by the given arguments.
        """
        return self.args(*args)
