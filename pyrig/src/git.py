"""GitHub repository utilities for token management and URL parsing.

This module provides utilities for working with GitHub repositories,
including authentication token retrieval, GitHub Actions environment
detection, and repository URL parsing.

The token retrieval supports both environment variables and .env files,
following a priority order that prefers environment variables for CI/CD
compatibility.
"""

import logging
import os
from functools import cache
from pathlib import Path
from subprocess import CompletedProcess  # nosec: B404
from urllib.parse import quote

from pyrig.src.modules.package import get_project_name_from_cwd
from pyrig.src.os.os import run_subprocess

logger = logging.getLogger(__name__)


@cache
def get_repo_remote_from_git(*, check: bool = True) -> str:
    """Get the remote origin URL from the local git repository.

    Executes `git config --get remote.origin.url` to retrieve the URL
    of the origin remote.
    Url can be:
        - https://github.com/owner/repo.git
        - git@github.com:owner/repo.git

    Args:
        check: Whether to check success in subprocess.

    Returns:
        The remote origin URL (e.g., "https://github.com/owner/repo.git"
        or "git@github.com:owner/repo.git").

    Raises:
        subprocess.CalledProcessError: If not in a git repository or if
            the origin remote is not configured.
    """
    stdout: str = run_subprocess(
        ["git", "config", "--get", "remote.origin.url"], check=check
    ).stdout.decode("utf-8")
    return stdout.strip()


@cache
def get_git_username() -> str:
    """Get the git username from the local git config.

    Executes `git config --get user.name` to retrieve the username.

    Returns:
        The git username.

    Raises:
        subprocess.CalledProcessError: If the username cannot be read.
    """
    stdout: str = run_subprocess(["git", "config", "--get", "user.name"]).stdout.decode(
        "utf-8"
    )
    return stdout.strip()


def get_repo_owner_and_name_from_git(
    *, check_repo_url: bool = True, url_encode: bool = False
) -> tuple[str, str]:
    """Extract the GitHub owner and repository name from the git remote.

    Parses the remote origin URL to extract the owner (organization or user)
    and repository name. Handles both HTTPS and SSH URL formats.

    Args:
        check_repo_url: Whether to check success in subprocess.
        url_encode: Whether to url encode the owner and repo name.

    Returns:
        A tuple of (owner, repository_name).

    Raises:
        subprocess.CalledProcessError: If the git remote cannot be read.

    Example:
        >>> owner, repo = get_repo_owner_and_name_from_git()
        >>> print(f"{owner}/{repo}")
        myorg/myrepo
    """
    url = get_repo_remote_from_git(check=check_repo_url)
    if not url:
        # we default to git username and repo name from cwd
        logger.debug("No git remote found, using git username and CWD for repo info")
        owner = get_git_username()
        repo = get_project_name_from_cwd()
        logger.debug("Derived repository: %s/%s", owner, repo)
        return owner, repo

    parts = url.removesuffix(".git").split("/")
    # keep last two parts
    owner, repo = parts[-2:]
    if ":" in owner:
        owner = owner.split(":")[-1]
    if url_encode:
        owner = quote(owner)
        repo = quote(repo)
    return owner, repo


def get_git_unstaged_changes() -> str:
    """Check if the git repository has uncommitted changes.

    Returns:
        The output of git diff
    """
    completed_process = run_subprocess(["git", "diff"])
    unstaged_changes: str = completed_process.stdout.decode("utf-8")
    return unstaged_changes


def git_add_file(path: Path, *, check: bool = True) -> CompletedProcess[bytes]:
    """Add a file to the git index.

    Args:
        path: Path to the file to add.
        check: Whether to check success in subprocess.

    Returns:
        The completed process result.
    """
    # make path relative to cwd if it is absolute
    if path.is_absolute():
        path = path.relative_to(Path.cwd())
    logger.debug("Adding file to git: %s", path)
    return run_subprocess(["git", "add", str(path)], check=check)


def get_repo_url_from_git() -> str:
    """Get the theoretical real github url.

    This is the url you would put in a browser not ssh.
    is like: https://github.com/owner/repo.git
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://github.com/{owner}/{repo}"


def get_github_pages_url_from_git() -> str:
    """Get the github pages url.

    This is the url you would put in a browser not ssh.
    is like: https://owner.github.io/repo
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://{owner}.github.io/{repo}"


def get_codecov_url_from_git() -> str:
    """Get the codecov url.

    This is the url you would put in a browser not ssh.
    is like: https://codecov.io/gh/owner/repo
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://codecov.io/gh/{owner}/{repo}"


def get_pypi_url_from_git() -> str:
    """Get the pypi url.

    This is the url you would put in a browser not ssh.
    is like: https://pypi.org/project/repo
    """
    _, repo = get_repo_owner_and_name_from_git(check_repo_url=False, url_encode=True)
    return f"https://pypi.org/project/{repo}"


def get_pypi_badge_url_from_git() -> str:
    """Get the pypi badge url.

    This is the url you would put in a browser not ssh.
    is like: https://img.shields.io/pypi/v/repo
    """
    _, repo = get_repo_owner_and_name_from_git(check_repo_url=False, url_encode=True)
    return f"https://img.shields.io/pypi/v/{repo}?logo=pypi&logoColor=white"


def get_workflow_run_url_from_git(workflow_name: str) -> str:
    """Get the workflow run url.

    This is the url you would put in a browser not ssh.
    is like: https://github.com/{repo_owner}/{repo_name}/actions/workflows/{workflow_name}.yaml
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://github.com/{owner}/{repo}/actions/workflows/{workflow_name}.yaml"


def get_workflow_badge_url_from_git(workflow_name: str, label: str, logo: str) -> str:
    """Get the workflow badge url.

    This is the url you would put in a browser not ssh.
    is like: https://img.shields.io/github/actions/workflow/status/{repo_owner}/{repo_name}/{workflow_name}.yaml?label=CI&logo=github
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow_name}.yaml?label={label}&logo={logo}"


def get_licence_badge_url_from_git() -> str:
    """Get the licence badge url.

    This is the url you would put in a browser not ssh.
    is like: https://img.shields.io/github/license/{repo_owner}/{repo_name}
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://img.shields.io/github/license/{owner}/{repo}"


def running_in_github_actions() -> bool:
    """Check if the code is running inside a GitHub Actions workflow.

    GitHub Actions sets the `GITHUB_ACTIONS` environment variable to "true"
    in all workflow runs. This function checks for that variable.

    Returns:
        True if running in GitHub Actions, False otherwise.

    Example:
        >>> if running_in_github_actions():
        ...     print("Running in CI")
        ... else:
        ...     print("Running locally")
    """
    return os.getenv("GITHUB_ACTIONS", "false") == "true"
