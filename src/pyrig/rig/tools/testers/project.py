"""Wrapper for the project's test runner and test-package layout conventions."""

from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class ProjectTester(Tool):
    """`pytest` wrapper and source of the project's test-package layout conventions.

    Beyond the badge and command metadata every `Tool` provides, this also
    exposes where the test suite lives, since its location follows a
    convention distinct from the source package layout.
    """

    def group(self) -> str:
        """Return `Group.TESTING`."""
        return Group.TESTING

    def image_url(self) -> str:
        """Return the badge image URL for `pytest`."""
        return (
            "https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest"
        )

    def link_url(self) -> str:
        """Return the URL of the pytest project page."""
        return "https://pytest.org"

    def name(self) -> str:
        """Return `'pytest'`."""
        return "pytest"

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return `('.pytest_cache/',)`."""
        return (".pytest_cache/",)

    def package_root(self) -> Path:
        """Return the path to the top-level tests package."""
        return self.source_root() / self.package_name()

    def package_name(self) -> str:
        """Return `'tests'`, the name of the top-level tests package."""
        return "tests"

    def source_root(self) -> Path:
        """Return the directory the tests package lives directly under.

        Returns `Path()`, meaning the tests package sits at the project
        root rather than under a source subdirectory such as `src/`.
        """
        return Path()

    def test_args(self, *args: str) -> Args:
        """Build a pytest command with the given arguments.

        Args:
            *args: Pytest command arguments to pass after the command name.

        Returns:
            Args starting with `'pytest'` followed by the given arguments.
        """
        return self.args(*args)
