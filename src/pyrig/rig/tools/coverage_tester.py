"""Coverage testing wrapper for the code coverage tool.

Wraps CoverageTester commands and information.
"""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.package_manager import PackageManager


class CoverageTester(Tool):
    """Pytest-cov configuration and static coverage badge.

    Constructs pytest-cov command arguments and builds a static shields.io
    coverage badge URL whose value and color are derived from the configured
    threshold.
    """

    def name(self) -> str:
        """Get the pytest-cov package name.

        Returns:
            'pytest-cov'
        """
        return "pytest-cov"

    def group(self) -> str:
        """Get the tool group this tester belongs to.

        Returns:
            'testing'
        """
        return Group.TESTING

    def image_url(self) -> str:
        """Return the badge image URL for this tool.

        The color is dynamically generated based on the coverage threshold:
        0% is red, 50% is yellow, and 100% is green.

        Returns:
            The URL of the badge image as a string.
        """
        hue, saturation, lightness = self.color()
        return f"https://img.shields.io/badge/coverage->={self.threshold()}%25-hsl({hue},{saturation}%25,{lightness}%25)?logo=codecov&logoColor=white"

    def link_url(self) -> str:
        """Return the link URL for this tool.

        Returns:
            The URL of the project page as a string.
        """
        return "https://github.com/pytest-dev/pytest-cov"

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return paths to ignore in version control."""
        return (".coverage",)

    def additional_test_args(self) -> Args:
        """Get pytest-cov arguments for local test runs.

        These arguments are added to ``[tool.pytest.ini_options] addopts`` in
        ``pyproject.toml``, so they apply to every local ``pytest`` invocation.

        Returns:
            Args: Tuple of pytest-cov CLI flags:
                ``--cov=<package_name>``: enables coverage tracking for the package.
                ``--cov-report=term-missing``: prints uncovered lines to the terminal.
                ``--cov-fail-under=<threshold>``: fails the run if coverage drops
                below the configured threshold.
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
        """Get the badge color derived from the coverage threshold.

        Interpolates the hue on a red-to-green spectrum where 0% coverage is
        red (hue 0), 50% is yellow (hue 60), and 100% is green (hue 120).

        Returns:
            Tuple of ``(hue, saturation, lightness)`` values.
        """
        hue = int((self.threshold() / 100) * 120)
        return hue, 80, 45

    def threshold(self) -> int:
        """Get the minimum required coverage percentage.

        Acts as the base default. Subclasses should override this method to
        enforce a stricter threshold for a specific project. For example,
        pyrig itself overrides this to 100.

        Returns:
            90
        """
        return 90
