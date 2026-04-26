"""Coverage testing wrapper for pytest-cov and Codecov.io integration.

Wraps pytest-cov configuration and Codecov.io URL construction to provide
a single, overridable interface for coverage analysis settings used across
local development and CI environments.
"""

from pyrig.rig.tools.base.tool import Tool, ToolGroup
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.version_controller import VersionController


class ProjectCoverageTester(Tool):
    """Pytest-cov configuration and Codecov.io integration.

    Constructs pytest-cov command arguments for local and CI coverage runs,
    and builds Codecov.io badge and dashboard URLs. The coverage threshold
    and package name are resolved dynamically, allowing subclasses to
    override individual settings without duplicating argument construction.

    Example:
        >>> ProjectCoverageTester.I.additional_args()
        ('--cov=mypackage', '--cov-report=term-missing', '--cov-fail-under=90')
        >>> ProjectCoverageTester.I.remote_coverage_url()
        'https://codecov.io/gh/owner/repo'
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
        return ToolGroup.TESTING

    def badge_urls(self) -> tuple[str, str]:
        """Get the Codecov badge image URL and dashboard URL.

        The badge image URL points to an SVG coverage badge on Codecov's CDN
        scoped to the default branch. The dashboard URL is the Codecov project
        page for the current repository.

        Returns:
            Tuple of (badge_image_url, dashboard_url), where badge_image_url
            is the SVG badge URL including the default branch, and dashboard_url
            is the Codecov project dashboard URL.
        """
        return (
            f"{self.remote_coverage_url()}/branch/{VersionController.I.default_branch()}/graph/badge.svg",
            self.remote_coverage_url(),
        )

    def additional_args(self) -> tuple[str, ...]:
        """Get pytest-cov arguments for local test runs.

        These arguments are added to ``[tool.pytest.ini_options] addopts`` in
        ``pyproject.toml``, so they apply to every local ``pytest`` invocation.

        Returns:
            Tuple of pytest-cov CLI flags:
                ``--cov=<package_name>``: enables coverage tracking for the package.
                ``--cov-report=term-missing``: prints uncovered lines to the terminal.
                ``--cov-fail-under=<threshold>``: fails the run if coverage drops
                below the configured threshold.
        """
        return (
            f"--cov={PackageManager.I.package_name()}",
            "--cov-report=term-missing",
            f"--cov-fail-under={self.coverage_threshold()}",
        )

    def additional_ci_args(self) -> tuple[str, ...]:
        """Get additional pytest-cov arguments for CI test runs.

        Added on top of ``additional_args()`` during CI execution to produce an
        XML coverage report, which is required for uploading results to Codecov.

        Returns:
            Tuple containing ``--cov-report=xml``.
        """
        return ("--cov-report=xml",)

    def coverage_threshold(self) -> int:
        """Get the minimum required coverage percentage.

        Acts as the base default. Subclasses should override this method to
        enforce a stricter threshold for a specific project. For example,
        pyrig itself overrides this to 100.

        Returns:
            90
        """
        return 90

    def remote_coverage_url(self) -> str:
        """Construct the Codecov project dashboard URL for the current repository.

        Resolves the repository owner and name from the git remote and
        URL-encodes both components to handle special characters safely.

        Returns:
            URL in the format ``https://codecov.io/gh/{owner}/{repo}``.
        """
        owner, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False, url_encode=True
        )
        return f"https://codecov.io/gh/{owner}/{repo}"

    def access_token_key(self) -> str:
        """Get the environment variable name for the Codecov upload token.

        This key is referenced in CI workflow definitions to inject the
        Codecov authentication token when uploading coverage reports.

        Returns:
            'CODECOV_TOKEN'
        """
        return "CODECOV_TOKEN"
