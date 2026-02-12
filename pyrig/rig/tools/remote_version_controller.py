"""GitHub remote version control wrapper.

Provides type-safe wrapper for GitHub remote version control operations.

Example:
    >>> from pyrig.rig.tools.remote_version_controller import (
        RemoteVersionController,
    )
    >>> RemoteVersionController.L.get_repo_url()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.rig.tools.version_controller import VersionController
from pyrig.src.string_ import make_linked_badge_markdown


class RemoteVersionController(Tool):
    """GitHub remote version control wrapper.

    Constructs GitHub things for repository, documentation, CI/CD, and badges.
    E.g. It constructs URLs and badge URLs for GitHub repository,
    documentation, CI/CD, and badges.
    Poetentially it could be extended to other remote version control systems.
    or to do more complex things.
    """

    @classmethod
    def get_name(cls) -> str:
        """Get tool name.

        Returns:
            'github'
        """
        return "github"

    @classmethod
    def get_group(cls) -> str:
        """Returns the group the tools belongs to.

        E.g. testing, tool, code-quality etc...
        """
        return ToolGroup.TOOLING

    @classmethod
    def get_badge_urls(cls) -> tuple[str, str]:
        """Returns the badge and connected page."""
        owner, repo = VersionController.L.get_repo_owner_and_name(
            check_repo_url=False, url_encode=True
        )
        return (
            f"https://img.shields.io/github/stars/{owner}/{repo}?style=social",
            cls.get_repo_url(),
        )

    @classmethod
    def get_dev_dependencies(cls) -> list[str]:
        """Get tool dependencies.

        Returns:
            List of tool dependencies.
        """
        return ["pygithub"]

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
    def get_cicd_url(cls, workflow_name: str) -> str:
        """Construct GitHub Actions workflow run URL.

        Args:
            workflow_name: Workflow file name without `.yml` extension.

        Returns:
            URL to workflow execution history.
        """
        return f"{cls.get_repo_url()}/actions/workflows/{workflow_name}.yml"

    @classmethod
    def get_cicd_badge_url(cls, workflow_name: str, label: str) -> str:
        """Construct GitHub Actions workflow status badge URL.

        Args:
            workflow_name: Workflow file name without `.yml` extension.
            label: Badge text label (e.g., "CI", "Build").
            logo: shields.io logo identifier (e.g., "github", "python").

        Returns:
            shields.io badge URL showing workflow status.
        """
        owner, repo = VersionController.L.get_repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow_name}.yml?label={label}&logo=github"

    @classmethod
    def get_cicd_badge(cls, workflow_name: str, label: str) -> str:
        """Construct GitHub Actions workflow status badge Markdown string.

        Args:
            workflow_name: Workflow file name without `.yml` extension.
            label: Badge text label (e.g., "CI", "Build").

        Returns:
            Markdown string for shields.io badge showing workflow status.
        """
        badge_url = cls.get_cicd_badge_url(workflow_name, label)
        cicd_url = cls.get_cicd_url(workflow_name)
        return make_linked_badge_markdown(
            badge_url=badge_url,
            link_url=cicd_url,
            alt_text=label,
        )
