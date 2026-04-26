"""Bandit security checker tool wrapper.

Provides a type-safe wrapper for constructing Bandit CLI commands.
Bandit finds common security issues in Python code by analysing ASTs.

Example:
    >>> from pyrig.rig.tools.security_checker import SecurityChecker
    >>> SecurityChecker.I.run_with_config_args().run()
"""

from collections.abc import Generator
from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester


class SecurityChecker(Tool):
    """Bandit security checker tool wrapper.

    Constructs Bandit CLI arguments for scanning Python source code for
    common security vulnerabilities. The primary entry point is
    ``run_with_config_args``, which reads Bandit settings from
    ``pyproject.toml`` and scans the project's source and test directories.

    Example:
        >>> SecurityChecker.I.run_with_config_args().run()
        >>> SecurityChecker.I.run_args("-r", "src/").run()
    """

    def name(self) -> str:
        """Get the tool command name.

        Returns:
            'bandit'
        """
        return "bandit"

    def group(self) -> str:
        """Get the badge group this tool belongs to.

        Returns:
            ``ToolGroup.SECURITY``
        """
        return ToolGroup.SECURITY

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge image URL and project page URL."""
        return (
            "https://img.shields.io/badge/security-bandit-yellow.svg",
            "https://github.com/PyCQA/bandit",
        )

    def run_with_config_args(self, *args: str) -> Args:
        """Construct Bandit arguments using ``pyproject.toml`` configuration.

        Passes ``-c pyproject.toml -r`` followed by each target path so that
        Bandit reads its settings from the project configuration file and
        recursively scans all relevant directories.

        Args:
            *args: Additional Bandit arguments appended after the target paths.

        Returns:
            Args for ``bandit -c pyproject.toml -r <package_root> <tests_root>``.
        """
        return self.run_args(
            "-c",
            "pyproject.toml",
            "-r",
            *self.target_posix_paths(),
            *args,
        )

    def run_args(self, *args: str) -> Args:
        """Construct bare Bandit arguments.

        Args:
            *args: Bandit command arguments.

        Returns:
            Args for ``bandit [args]``.
        """
        return self.args(*args)

    def target_posix_paths(self) -> Generator[str, None, None]:
        """Yield the target scan paths as POSIX strings.

        Converts each path from ``target_paths`` to its POSIX string
        representation, which Bandit expects on the command line.

        Yields:
            POSIX path string for each target scan directory.
        """
        return (path.as_posix() for path in self.target_paths())

    def target_paths(self) -> tuple[Path, ...]:
        """Return the directories that Bandit should scan.

        Combines the project's source package root and tests package root so
        that both application code and test code are checked for security
        issues.

        Returns:
            Tuple of ``Path`` objects: ``(package_root, tests_package_root)``.
        """
        return (
            PackageManager.I.package_root(),
            ProjectTester.I.tests_package_root(),
        )
