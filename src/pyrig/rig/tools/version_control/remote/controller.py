"""Identity, URL, and environment metadata for a repository's remote hosting service."""

import os
from pathlib import Path

from pyrig.core.strings import make_linked_badge_markdown
from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.controller import VersionController


class RemoteVersionController(Tool):
    """GitHub tool for repository identity, URLs, and environment metadata.

    Builds the repository page, issues tracker, releases, and GitHub
    Actions workflow URLs, plus the badge and access-token metadata
    needed to reference them from README and workflow files. Also
    resolves GitHub's `.github` config directory, detects the GitHub
    Actions CI environment, and builds `gh` CLI commands.
    """

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return an empty tuple; `gh` is a system dependency, not a pip package."""
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

    def args(self, *args: str) -> Args:
        """Build an `Args` command starting with `gh`, the GitHub CLI.

        Overrides the base implementation, which would otherwise start the
        command with `name()` (`"github"`, used for badges and the
        `.github` config directory, not an executable).

        Args:
            *args: Command arguments to follow `gh`.

        Returns:
            An `Args` object whose first element is `gh`.
        """
        return Args("gh", *args)

    def release_args(self, *args: str) -> Args:
        """Build base arguments for `gh release`.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `gh release [args]`.
        """
        return self.args("release", *args)

    def create_release_args(self, *args: str, tag: str) -> Args:
        """Build arguments to create a GitHub release for a tag.

        Args:
            *args: Additional arguments appended to the command.
            tag: The tag to release, also used as the release title.

        Returns:
            Args for `gh release create <tag> --title=<tag> --generate-notes
            [args]`.
        """
        return self.release_args(
            "create",
            tag,
            f"--title={tag}",
            "--generate-notes",
            *args,
        )

    def api_args(self, *args: str, endpoint: str) -> Args:
        """Build arguments for `gh api`, meant for embedding in shell scripts.

        Callers are responsible for quoting `endpoint` themselves if it
        contains a shell variable expansion that must survive word
        splitting once expanded at runtime (e.g. `'"repos/${repo}"'`).

        Args:
            *args: Additional arguments appended to the command, e.g.
                `"--input=-"`.
            endpoint: The GitHub API endpoint path.

        Returns:
            Args for `gh api <endpoint> [args]`.
        """
        return self.args("api", endpoint, *args)

    def api_method_args(self, *args: str, endpoint: str, method: str) -> Args:
        """Build arguments for `gh api` with an HTTP method, for shell scripts.

        Callers are responsible for quoting `endpoint` and `method`
        themselves if either contains a shell variable expansion.

        Args:
            *args: Additional arguments appended to the command.
            endpoint: The GitHub API endpoint path.
            method: The HTTP method, e.g. `"PATCH"` or `'"${method}"'` if
                it's a shell variable expansion.

        Returns:
            Args for `gh api <endpoint> --method=<method> [args]`.
        """
        return self.api_args(f"--method={method}", *args, endpoint=endpoint)

    def api_method_input_args(
        self,
        *args: str,
        endpoint: str,
        method: str,
        input_: str,
    ) -> Args:
        """Build arguments for `gh api` with a method and request body input.

        Args:
            *args: Additional arguments appended to the command.
            endpoint: The GitHub API endpoint path.
            method: The HTTP method, e.g. `"PATCH"` or `'"${method}"'` if
                it's a shell variable expansion.
            input_: Value for `--input`, e.g. `"-"` to read the request
                body from stdin.

        Returns:
            Args for `gh api <endpoint> --method=<method> --input=<input_>
            [args]`.
        """
        return self.api_method_args(
            f"--input={input_}",
            *args,
            endpoint=endpoint,
            method=method,
        )
