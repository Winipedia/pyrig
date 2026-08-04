"""Identity, URL, and environment metadata for a repository's remote hosting service."""

import os
from pathlib import Path

from pyrig.core.strings import make_linked_badge_markdown
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.controller import VersionController


class RemoteVersionController(Tool):
    """GitHub tool for repository identity, URLs, and environment metadata.

    Builds the repository page, issues tracker, releases, and GitHub
    Actions workflow URLs, plus the badge and access-token metadata
    needed to reference them from README and workflow files. Also
    resolves GitHub's `.github` config directory and detects the
    GitHub Actions CI environment.
    """

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return an empty tuple; GitHub is not installed as a Python package."""
        return ()

    def group(self) -> str:
        """Return `Group.TOOLING` as the badge category."""
        return Group.TOOLING

    def image_url(self) -> str:
        """Return the shields.io badge image URL showing the repository's star count.

        Returns:
            URL in the format
            `https://img.shields.io/github/stars/{owner}/{repo}?style=social`.
        """
        return f"https://img.shields.io/github/stars/{self.repository()}?style=social"

    def link_url(self) -> str:
        """Return the GitHub repository page URL."""
        return self.repo_url()

    def name(self) -> str:
        """Return `'github'` as the executable name."""
        return "github"

    def cicd_badge(self, workflow_name: str, label: str) -> str:
        """Construct a clickable Markdown badge for a GitHub Actions workflow status.

        Args:
            workflow_name: Workflow file name without the `.yml` extension.
            label: Display label shown on the badge (e.g., "CI", "Build").

        Returns:
            Markdown string in the form `[![label](badge_url)](cicd_url)`.
        """
        badge_url = self.cicd_badge_url(workflow_name, label)
        cicd_url = self.cicd_url(workflow_name)
        return make_linked_badge_markdown(
            image_url=badge_url,
            link_url=cicd_url,
            alt_text=label,
        )

    def issues_url(self) -> str:
        """Construct the GitHub issues URL.

        Returns:
            URL in the format `https://github.com/{owner}/{repo}/issues`.
        """
        return f"{self.repo_url()}/issues"

    def releases_url(self) -> str:
        """Construct the GitHub releases URL.

        Returns:
            URL in the format `https://github.com/{owner}/{repo}/releases`.
        """
        return f"{self.repo_url()}/releases"

    def cicd_url(self, workflow_name: str) -> str:
        """Construct the GitHub Actions workflow run history URL.

        Args:
            workflow_name: Workflow file name without the `.yml` extension.

        Returns:
            URL in the format
            `https://github.com/{owner}/{repo}/actions/workflows/{workflow_name}.yml`.
        """
        return f"{self.repo_url()}/actions/workflows/{workflow_name}.yml"

    def cicd_badge_url(self, workflow_name: str, label: str) -> str:
        """Construct a shields.io badge URL for a GitHub Actions workflow status.

        Args:
            workflow_name: Workflow file name without the `.yml` extension.
            label: Display label shown on the badge (e.g., "CI", "Build").

        Returns:
            shields.io URL that renders the current workflow status as a badge.
        """
        return f"https://img.shields.io/github/actions/workflow/status/{self.repository()}/{workflow_name}.yml?label={label}&logo=github"

    def repo_url(self) -> str:
        """Construct the HTTPS GitHub repository URL.

        Returns:
            URL in the format `https://github.com/{owner}/{repo}`.
        """
        return f"{self.url_base()}/{self.repository()}"

    def security_advisory_url(self) -> str:
        """Construct the URL for filing a new private security advisory.

        Returns:
            URL in the format
            `https://github.com/{owner}/{repo}/security/advisories/new`.
        """
        return f"{self.repo_url()}/security/advisories/new"

    def repository(self) -> str:
        """Return `"owner/repo"` for this repository.

        Returns:
            The repository owner and project name joined with `/`.
        """
        return f"{VersionController.I.repo_owner()}/{PackageManager.I.project_name()}"

    def url_base(self) -> str:
        """Return `'https://github.com'` as GitHub's base URL."""
        return "https://github.com"

    def config_dir(self) -> Path:
        """Return GitHub's special repository configuration directory.

        Returns:
            `Path(".github")`, the directory GitHub reads workflows, issue
            templates, the pull request template, repository settings, and
            `CODEOWNERS` from.
        """
        return Path(f".{self.name()}")

    def access_token_key(self) -> str:
        """Return `'REPO_TOKEN'` as the access token's environment variable name."""
        return "REPO_TOKEN"

    def running_in_ci(self) -> bool:
        """Detect whether the code is running inside a GitHub Actions environment.

        Checks the `GITHUB_ACTIONS` environment variable, which GitHub Actions
        automatically sets to `"true"` for all workflow runs.

        Returns:
            `True` if running inside GitHub Actions, `False` otherwise.
        """
        return os.getenv("GITHUB_ACTIONS", "false") == "true"
