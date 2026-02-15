"""Pytest-cov coverage testing wrapper.

Provides type-safe wrapper for pytest-cov commands for code coverage analysis.
Shows coverage badge from Codecov.io.

Example:
    >>> from pyrig.rig.tools.project_coverage_tester import (
    ...     ProjectCoverageTester,
    ... )
    >>> ProjectCoverageTester.I.remote_coverage_url()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.rig.tools.version_controller import VersionController


class ProjectCoverageTester(Tool):
    """Pytest-cov coverage testing wrapper.

    Constructs pytest-cov command arguments for code coverage analysis.
    Integrates with Codecov.io for badge and coverage tracking.

    Operations:
        - Code coverage analysis
        - Coverage badge generation
        - Coverage integration with remote services

    Example:
        >>> ProjectCoverageTester.I.remote_coverage_url()
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'pytest-cov'
        """
        return "pytest-cov"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            'testing'
        """
        return ToolGroup.TESTING

    def badge_urls(self) -> tuple[str, str]:
        

        Returns:
            Tuple of two strings: (badge_image_url, badge_link_url).
        """Get Codecov coverage badge image URL and dashboard URL."""
        return (
            f"{self.remote_coverage_url()}/branch/{VersionController.I.default_branch()}/graph/badge.svg",
            self.remote_coverage_url(),
        )

    def remote_coverage_url(self) -> str:
        """Construct Codecov dashboard URL.

        Returns:
            URL in format: `https://codecov.io/gh/{owner}/{repo}`
        """
        owner, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False, url_encode=True
        )
        return f"https://codecov.io/gh/{owner}/{repo}"
