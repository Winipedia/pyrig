"""Remote version controller wrapper.

Wraps RemoteVersionController commands and information.
"""

import os

from pyrig.core.strings import make_linked_badge_markdown
from pyrig.rig.tools.base.tool import Tool, ToolGroup
from pyrig.rig.tools.version_control.version_controller import VersionController


class RemoteVersionController(Tool):
    """GitHub tool for constructing repository URLs and badges.

    Implements the Tool interface for GitHub, providing methods to build
    URLs for the repository, issues tracker, releases, and GitHub Actions
    workflows. Also supports shields.io badge generation for use in
    README and documentation files.
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'github'
        """
        return "github"

    def group(self) -> str:
        """Get the badge group this tool belongs to.

        Returns:
            `ToolGroup.TOOLING`
        """
        return ToolGroup.TOOLING

    def badge_urls(self) -> tuple[str, str]:
        """Return the GitHub star-count badge image URL and repository page URL.

        Returns:
            Tuple of (badge_image_url, link_url) where the badge image shows
            the repository star count using the shields.io social style.
        """
        owner, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False, url_encode=True
        )
        return (
            f"https://img.shields.io/github/stars/{owner}/{repo}?style=social",
            self.repo_url(),
        )

    def dev_dependencies(self) -> tuple[str, ...]:
        """Get tool development dependencies.

        Returns:
            Tuple containing 'pygithub'.
        """
        return ("pygithub",)

    def cicd_badge(self, workflow_name: str, label: str) -> str:
        """Construct a clickable Markdown badge for a GitHub Actions workflow status.

        Combines the shields.io badge image URL and the workflow run history URL
        into a single Markdown badge string.

        Args:
            workflow_name: Workflow file name without the `.yml` extension.
            label: Display label shown on the badge (e.g., "CI", "Build").

        Returns:
            Markdown string in the form ``[![label](badge_url)](cicd_url)``.
        """
        badge_url = self.cicd_badge_url(workflow_name, label)
        cicd_url = self.cicd_url(workflow_name)
        return make_linked_badge_markdown(
            badge_url=badge_url,
            link_url=cicd_url,
            alt_text=label,
        )

    def issues_url(self) -> str:
        """Construct the GitHub issues URL.

        Returns:
            URL in the format ``https://github.com/{owner}/{repo}/issues``.
        """
        return f"{self.repo_url()}/issues"

    def releases_url(self) -> str:
        """Construct the GitHub releases URL.

        Returns:
            URL in the format ``https://github.com/{owner}/{repo}/releases``.
        """
        return f"{self.repo_url()}/releases"

    def cicd_url(self, workflow_name: str) -> str:
        """Construct the GitHub Actions workflow run history URL.

        Args:
            workflow_name: Workflow file name without the `.yml` extension.

        Returns:
            URL in the format
            ``https://github.com/{owner}/{repo}/actions/workflows/{workflow_name}.yml``.
        """
        return f"{self.repo_url()}/actions/workflows/{workflow_name}.yml"

    def cicd_badge_url(self, workflow_name: str, label: str) -> str:
        """Construct a shields.io badge URL for a GitHub Actions workflow status.

        Args:
            workflow_name: Workflow file name without the `.yml` extension.
            label: Badge label text (e.g., "CI", "Build").

        Returns:
            shields.io URL that renders the current workflow status as a badge.
        """
        owner, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow_name}.yml?label={label}&logo=github"

    def repo_url(self) -> str:
        """Construct the HTTPS GitHub repository URL.

        Returns:
            URL in the format ``https://github.com/{owner}/{repo}``.
        """
        owner, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"{self.url_base()}/{owner}/{repo}"

    def url_base(self) -> str:
        """Get the base URL for GitHub.

        Returns:
            ``https://github.com``
        """
        return "https://github.com"

    def running_in_ci(self) -> bool:
        """Detect whether the code is running inside a GitHub Actions environment.

        Checks the ``GITHUB_ACTIONS`` environment variable, which GitHub
        Actions automatically sets to ``"true"`` for all workflow runs.

        Returns:
            True if running inside GitHub Actions, False otherwise.
        """
        return os.getenv("GITHUB_ACTIONS", "false") == "true"

    def access_token_key(self) -> str:
        """Get the environment variable name for the repository access token.

        This key is used to retrieve the GitHub token from the environment
        during CI/CD workflow runs and branch protection operations.

        Returns:
            ``'REPO_TOKEN'``
        """
        return "REPO_TOKEN"
