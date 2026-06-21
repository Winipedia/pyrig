"""Project tester wrapper.

Wraps ProjectTester commands and information.
"""

from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class ProjectTester(Tool):
    """Pytest runner and test-layout configuration.

    Centralizes test-related constants (package name, source root, module
    prefix) used throughout the project for path resolution, config
    generation, and mirror-test discovery. Also constructs pytest command
    Args objects for both local and CI execution.
    """

    def name(self) -> str:
        """Get the pytest command name.

        Returns:
            'pytest'
        """
        return "pytest"

    def group(self) -> str:
        """Get the tool group for this tool."""
        return Group.TESTING

    def image_url(self) -> str:
        """Return the badge image URL for this tool.

        Returns:
            The URL of the badge image as a string.
        """
        return (
            "https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest"
        )

    def link_url(self) -> str:
        """Return the link URL for this tool.

        Returns:
            The URL of the pytest project page as a string.
        """
        return "https://pytest.org"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Adds pyrig-fixtures to the pytest as a dev dependency."""
        return (*super().dev_dependencies(), "pyrig-fixtures")

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return paths to ignore in version control."""
        return (".pytest_cache/",)

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

    def test_args(self, *args: str) -> Args:
        """Construct pytest command arguments to run tests.

        Prepends the ``pytest`` command name to the given arguments.

        Args:
            *args: Pytest command arguments to pass after the command name.

        Returns:
            Args starting with ``'pytest'`` followed by the given arguments.
        """
        return self.args(*args)
