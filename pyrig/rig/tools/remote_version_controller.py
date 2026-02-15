"""GitHub remote version control wrapper.

Provides type-safe wrapper for GitHub remote version control operations.

Example:
    >>> from pyrig.rig.tools.remote_version_controller import (
    ...     RemoteVersionController,
    ... )
    >>> RemoteVersionController.I.repo_url()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.rig.tools.version_controller import VersionController
from pyrig.src.string_ import make_linked_badge_markdown


class RemoteVersionController(Tool):
    """GitHub remote version control wrapper.

    Constructs URLs and badge URLs for GitHub repository, documentation,
    CI/CD, and badges. Potentially extensible to other remote version
    control systems.
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'github'
        """
        return "github"

    def group(self) -> str:
        """Get badge group.

        Returns:
            `ToolGroup.TOOLING`
        """
        return ToolGroup.TOOLING

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge image URL and repository page URL."""
        owner, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False, url_encode=True
        )
        return (
            f"https://img.shields.io/github/stars/{owner}/{repo}?style=social",
            self.repo_url(),
        )

    def dev_dependencies(self) -> list[str]:
        """Get tool dependencies.

        Returns:
            List of tool dependencies.
        """
        return ["pygithub"]

    def url_base(self) -> str:
        """Get the base URL for GitHub.

        Returns:
            Base URL: https://github.com
        """
        return "https://github.com"

    def repo_url(self) -> str:
        """Construct HTTPS GitHub repository URL.

        Returns:
            URL in format: `https://github.com/{owner}/{repo}`
        """
        owner, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"{self.url_base()}/{owner}/{repo}"

    def issues_url(self) -> str:
        """Construct GitHub issues URL.

        Returns:
            URL in format: `https://github.com/{owner}/{repo}/issues`
        """
        return f"{self.repo_url()}/issues"

    def releases_url(self) -> str:
        """Construct GitHub releases URL.

        Returns:
            URL in format: `https://github.com/{owner}/{repo}/releases`
        """
        return f"{self.repo_url()}/releases"

    def cicd_url(self, workflow_name: str) -> str:
        """Construct GitHub Actions workflow run URL.

        Args:
            workflow_name: WorkflowConfigFile file name without `.yml` extension.

        Returns:
            URL to workflow execution history.
        """
        return f"{self.repo_url()}/actions/workflows/{workflow_name}.yml"

    def cicd_badge_url(self, workflow_name: str, label: str) -> str:
        """Construct GitHub Actions workflow status badge URL.

        Args:
            workflow_name: WorkflowConfigFile file name without `.yml` extension.
            label: Badge text label (e.g., "CI", "Build").

        Returns:
            shields.io badge URL showing workflow status.
        """
        owner, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow_name}.yml?label={label}&logo=github"

    def cicd_badge(self, workflow_name: str, label: str) -> str:
        """Construct GitHub Actions workflow status badge Markdown string.

        Args:
            workflow_name: WorkflowConfigFile file name without `.yml` extension.
            label: Badge text label (e.g., "CI", "Build").

        Returns:
            Markdown string for shields.io badge showing workflow status.
        """
        badge_url = self.cicd_badge_url(workflow_name, label)
        cicd_url = self.cicd_url(workflow_name)
        return make_linked_badge_markdown(
            badge_url=badge_url,
            link_url=cicd_url,
            alt_text=label,
        )
