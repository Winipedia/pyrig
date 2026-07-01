"""Pytest-cov command construction and coverage badge generation."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.package_manager import PackageManager


class CoverageTester(Tool):
    """Pytest-cov configuration and static coverage badge.

    Constructs pytest-cov command arguments and builds a static shields.io
    coverage badge URL whose label and color are derived from the required
    coverage threshold.
    """

    def name(self) -> str:
        """Return `'pytest-cov'`."""
        return "pytest-cov"

    def group(self) -> str:
        """Return `Group.TESTING`."""
        return Group.TESTING

    def image_url(self) -> str:
        """Return the badge image URL, with a label and color set by the threshold."""
        hue, saturation, lightness = self.color()
        return f"https://img.shields.io/badge/coverage->={self.threshold()}%25-hsl({hue},{saturation}%25,{lightness}%25)?logo=codecov&logoColor=white"

    def link_url(self) -> str:
        """Return the URL of the pytest-cov project page."""
        return "https://github.com/pytest-dev/pytest-cov"

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return `(".coverage",)`."""
        return (".coverage",)

    def additional_test_args(self) -> Args:
        """Return the pytest-cov CLI flags for a coverage-enabled test run.

        Enables branch coverage tracking for the project's package, prints
        uncovered lines, and fails the run if coverage drops below the
        threshold.

        Returns:
            The pytest-cov CLI flags to run with.
        """
        return Args(
            (
                f"--cov={PackageManager.I.package_name()}",
                "--cov-branch",
                "--cov-report=term-missing",
                f"--cov-fail-under={self.threshold()}",
            )
        )

    def color(self) -> tuple[int, int, int]:
        """Return the badge color derived from the coverage threshold.

        Interpolates the hue on a red-to-green spectrum where 0% coverage is
        red (hue 0), 50% is yellow (hue 60), and 100% is green (hue 120).

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
