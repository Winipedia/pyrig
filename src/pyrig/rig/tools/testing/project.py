"""Wrapper for the project's test runner and test-package layout conventions."""

from pathlib import Path

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.packages.manager import PackageManager


class ProjectTester(Tool):
    """`pytest` wrapper and source of the project's test-package layout conventions.

    Beyond the badge and command metadata every `Tool` provides, this also
    exposes where the test suite lives, since its location follows a
    convention distinct from the source package layout.
    """

    def group(self) -> str:
        """Return `Group.TESTING`."""
        return Group.PROJECT_STATUS

    def image_url(self) -> str:
        """Return the badge image URL, with a label and color set by the threshold."""
        hue, saturation, lightness = self.color()
        return f"https://img.shields.io/badge/coverage->={self.threshold()}%25-hsl({hue},{saturation}%25,{lightness}%25)?logo=codecov&logoColor=white"

    def link_url(self) -> str:
        """Return the URL of the pytest project page."""
        return "https://pytest.org"

    def name(self) -> str:
        """Return `'pytest'`."""
        return "pytest"

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return `('pytest', 'pytest-cov')`."""
        return (*super().dev_dependencies(), "pytest-cov", "pytest-randomly")

    def version_control_ignore_patterns(self) -> tuple[str, ...]:
        """Return `('.pytest_cache/',)`."""
        return (".pytest_cache/", ".coverage")

    def color(self) -> tuple[int, int, int]:
        """Return the badge color derived from the coverage threshold.

        Interpolates the hue on a red-to-green spectrum where a threshold of
        0% is red (hue 0), 50% is yellow (hue 60), and 100% is green (hue 120).

        Returns:
            An `(hue, saturation, lightness)` tuple.
        """
        hue = int((self.threshold() / 100) * 120)
        return hue, 80, 45

    def threshold(self) -> int:
        """Return the minimum required coverage percentage.

        Subclasses may override this to enforce a different threshold.

        Returns:
            90
        """
        return 90

    def additional_args(self) -> Args:
        """Return additional pytest command arguments to include in the config.

        This hook exists to allow overriding and therefore easier integration
        for pytest plugins and flags that do not support configuration via
        `pyproject.toml`.

        Returns:
            The pytest-cov CLI flags to append to the test run.
        """
        return Args(
            f"--cov={PackageManager.I.package_name()}",
            "--cov-branch",
            f"--cov-fail-under={self.threshold()}",
            "--cov-report=term-missing:skip-covered",
        )

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
