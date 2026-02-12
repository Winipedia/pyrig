"""Pytest-cov coverage testing wrapper.

Provides type-safe wrapper for pytest-cov commands for code coverage analysis.
Shows coverage badge from Codecov.io.

Example:
    >>> from pyrig.rig.tools.project_coverage_tester import (
        ProjectCoverageTester,
    )
    >>> ProjectCoverageTester.L.get_remote_coverage_url()
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
        >>> ProjectCoverageTester.L.get_remote_coverage_url()
    """

    @classmethod
    def get_name(cls) -> str:
        """Get tool name.

        Returns:
            'pytest-cov'
        """
        return "pytest-cov"

    @classmethod
    def get_group(cls) -> str:
        """Returns the group the tools belongs to.

        E.g. testing, tool, code-quality etc...
        """
        return ToolGroup.TESTING

    @classmethod
    def get_badge_urls(cls) -> tuple[str, str]:
        """Returns the badge and connected page."""
        return (
            f"{cls.get_remote_coverage_url()}/branch/{VersionController.L.get_default_branch()}/graph/badge.svg",
            cls.get_remote_coverage_url(),
        )

    @classmethod
    def get_remote_coverage_url(cls) -> str:
        """Construct Codecov dashboard URL.

        Returns:
            URL in format: `https://codecov.io/gh/{owner}/{repo}`
        """
        owner, repo = VersionController.L.get_repo_owner_and_name(
            check_repo_url=False, url_encode=True
        )
        return f"https://codecov.io/gh/{owner}/{repo}"
