"""GitHub remote version control wrapper.

Provides type-safe wrapper for GitHub remote version control operations.

Example:
    >>> from pyrig.dev.management.remote_version_controller import (
        RemoteVersionController,
    )
    >>> RemoteVersionController.L.get_repo_url()
    >>> RemoteVersionController.L.get_documentation_url()
"""

from pyrig.dev.management.base.base import Tool
from pyrig.dev.management.version_controller import VersionController


class RemoteVersionController(Tool):
    """GitHub remote version control wrapper.

    Constructs GitHub things for repository, documentation, CI/CD, and badges.
    E.g. It constructs URLs and badge URLs for GitHub repository,
    documentation, CI/CD, and badges.
    Poetentially it could be extended to other remote version control systems.
    or to do more complex things.
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'github'
        """
        return "github"

    @classmethod
    def get_url_base(cls) -> str:
        """Get the base URL for GitHub.

        Returns:
            Base URL: https://github.com
        """
        return "https://github.com"

    @classmethod
    def get_repo_url(cls) -> str:
        """Construct HTTPS GitHub repository URL.

        Returns:
            URL in format: `https://github.com/{owner}/{repo}`
        """
        owner, repo = VersionController.L.get_repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"{cls.get_url_base()}/{owner}/{repo}"

    @classmethod
    def get_issues_url(cls) -> str:
        """Construct GitHub issues URL.

        Returns:
            URL in format: `https://github.com/{owner}/{repo}/issues`
        """
        return f"{cls.get_repo_url()}/issues"

    @classmethod
    def get_releases_url(cls) -> str:
        """Construct GitHub releases URL.

        Returns:
            URL in format: `https://github.com/{owner}/{repo}/releases`
        """
        return f"{cls.get_repo_url()}/releases"

    @classmethod
    def get_documentation_url(cls) -> str:
        """Construct GitHub Pages URL.

        Returns:
            URL in format: `https://{owner}.github.io/{repo}`

        Note:
            Site may not exist if GitHub Pages not enabled.
        """
        owner, repo = VersionController.L.get_repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"https://{owner}.github.io/{repo}"

    @classmethod
    def get_cicd_url(cls, workflow_name: str) -> str:
        """Construct GitHub Actions workflow run URL.

        Args:
            workflow_name: Workflow file name without `.yaml` extension.

        Returns:
            URL to workflow execution history.
        """
        return f"{cls.get_repo_url()}/actions/workflows/{workflow_name}.yaml"

    @classmethod
    def get_cicd_badge_url(cls, workflow_name: str, label: str, logo: str) -> str:
        """Construct GitHub Actions workflow status badge URL.

        Args:
            workflow_name: Workflow file name without `.yaml` extension.
            label: Badge text label (e.g., "CI", "Build").
            logo: shields.io logo identifier (e.g., "github", "python").

        Returns:
            shields.io badge URL showing workflow status.
        """
        owner, repo = VersionController.L.get_repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow_name}.yaml?label={label}&logo={logo}"

    @classmethod
    def get_license_badge_url(cls) -> str:
        """Construct GitHub license badge URL.

        Returns:
            shields.io badge URL showing repository license.
        """
        owner, repo = VersionController.L.get_repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"https://img.shields.io/github/license/{owner}/{repo}"
