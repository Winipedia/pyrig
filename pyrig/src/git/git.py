"""GitHub repository utilities for token management and URL parsing.

This module provides utilities for working with GitHub repositories,
including authentication token retrieval, GitHub Actions environment
detection, and repository URL parsing.

The token retrieval supports both environment variables and .env files,
following a priority order that prefers environment variables for CI/CD
compatibility.

Example:
    >>> from pyrig.src.git.github.github import get_repo_owner_and_name_from_git
    >>> owner, repo = get_repo_owner_and_name_from_git()
    >>> print(f"{owner}/{repo}")
    myorg/myrepo
"""

import os
from pathlib import Path
from subprocess import CompletedProcess  # nosec: B404

from pyrig.src.modules.package import get_project_name_from_cwd
from pyrig.src.os.os import run_subprocess


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


def get_repo_url_from_git(*, check: bool = True) -> str:
    """Get the remote origin URL from the local git repository.

    Executes `git config --get remote.origin.url` to retrieve the URL
    of the origin remote.
    Url can be:
        - https://github.com/owner/repo.git
        - git@github.com:owner/repo.git

    Args:
        check: Whether to check succes in subprocess.

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


def get_repo_owner_and_name_from_git(*, check_repo_url: bool = True) -> tuple[str, str]:
    """Extract the GitHub owner and repository name from the git remote.

    Parses the remote origin URL to extract the owner (organization or user)
    and repository name. Handles both HTTPS and SSH URL formats.

    Args:
        check_repo_url: Whether to check succes in subprocess.

    Returns:
        A tuple of (owner, repository_name).

    Raises:
        subprocess.CalledProcessError: If the git remote cannot be read.

    Example:
        >>> owner, repo = get_repo_owner_and_name_from_git()
        >>> print(f"{owner}/{repo}")
        myorg/myrepo
    """
    url = get_repo_url_from_git(check=check_repo_url)
    if not url:
        # we default to git username and repo name from cwd
        owner = get_git_username()
        repo = get_project_name_from_cwd()
        return owner, repo

    parts = url.removesuffix(".git").split("/")
    # keep last two parts
    owner, repo = parts[-2:]
    if ":" in owner:
        owner = owner.split(":")[-1]
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
        check: Whether to check succes in subprocess.

    Returns:
        The completed process result.
    """
    # make path relative to cwd if it is absolute
    if path.is_absolute():
        path = path.relative_to(Path.cwd())
    return run_subprocess(["git", "add", str(path)], check=check)
