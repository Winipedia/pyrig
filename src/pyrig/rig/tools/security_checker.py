"""Security scanner command construction and badge metadata."""

from collections.abc import Iterator
from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.testers.project import ProjectTester


class SecurityChecker(Tool):
    """Wrapper for the `bandit` security checker.

    Constructs `bandit` command-line arguments for scanning the project's
    source and test code for common security vulnerabilities.
    """

    def name(self) -> str:
        """Return `'bandit'`."""
        return "bandit"

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for `bandit`."""
        return "https://img.shields.io/badge/security-bandit-yellow.svg"

    def link_url(self) -> str:
        """Return the URL of the `bandit` project page."""
        return "https://github.com/PyCQA/bandit"

    def run_with_config_args(self, *args: str) -> Args:
        """Construct `bandit` arguments that scan using `pyproject.toml` configuration.

        Args:
            *args: Additional arguments appended after the scan target paths.

        Returns:
            Args for `bandit -c pyproject.toml -r <target paths> [args]`.
        """
        return self.run_args(
            "-c",
            "pyproject.toml",
            "-r",
            *self.target_posix_paths(),
            *args,
        )

    def run_args(self, *args: str) -> Args:
        """Construct bare `bandit` arguments.

        Args:
            *args: `bandit` command arguments.

        Returns:
            Args for `bandit [args]`.
        """
        return self.args(*args)

    def target_posix_paths(self) -> Iterator[str]:
        """Yield the target scan paths as POSIX strings.

        Yields:
            A POSIX path string for each target scan directory.
        """
        return (path.as_posix() for path in self.target_paths())

    def target_paths(self) -> tuple[Path, ...]:
        """Return the directories to scan for security issues.

        Returns:
            The project's source package root and tests package root.
        """
        return (
            PackageManager.I.package_root(),
            ProjectTester.I.tests_package_root(),
        )
