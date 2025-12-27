"""Git repository utilities for URL parsing and GitHub integration.

Provides utilities for extracting repository information from git config and generating
GitHub-related URLs (Pages, PyPI, badges, workflows).
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
    """Get the remote origin URL from git config.

    Args:
        check: Whether to raise exception if command fails.

    Returns:
        Remote origin URL (HTTPS or SSH format).
        Empty string if check=False and no remote.

    Raises:
        subprocess.CalledProcessError: If check=True and command fails.
    """
    stdout: str = run_subprocess(
        ["git", "config", "--get", "remote.origin.url"], check=check
    ).stdout.decode("utf-8")
    return stdout.strip()


@cache
def get_git_username() -> str:
    """Get git username from local config.

    Returns:
        Configured git username (cached).

    Raises:
        subprocess.CalledProcessError: If user.name not configured.
    """
    stdout: str = run_subprocess(["git", "config", "--get", "user.name"]).stdout.decode(
        "utf-8"
    )
    return stdout.strip()


def get_repo_owner_and_name_from_git(
    *, check_repo_url: bool = True, url_encode: bool = False
) -> tuple[str, str]:
    """Extract GitHub owner and repository name from git remote URL.

    Parses remote origin URL (HTTPS or SSH format). Falls back to git username
    and current directory name if no remote configured.

    Args:
        check_repo_url: Whether to raise exception if remote cannot be read.
        url_encode: Whether to URL-encode owner and repo names.

    Returns:
        Tuple of (owner, repository_name).

    Raises:
        subprocess.CalledProcessError: If check_repo_url=True and remote unreadable.
    """
    url = get_repo_remote_from_git(check=check_repo_url)
    if not url:
        # we default to git username and repo name from cwd
        logger.debug("No git remote found, using git username and CWD for repo info")
        owner = get_git_username()
        repo = get_project_name_from_cwd()
        logger.debug("Derived repository: %s/%s", owner, repo)
    else:
        parts = url.removesuffix(".git").split("/")
        # keep last two parts
        owner, repo = parts[-2:]
        if ":" in owner:
            owner = owner.split(":")[-1]
    if url_encode:
        logger.debug("Url encoding owner and repo")
        owner = quote(owner)
        repo = quote(repo)
    return owner, repo


def get_git_unstaged_changes() -> str:
    """Get diff of unstaged changes.

    Returns:
        Output of `git diff` (empty string if no changes).

    Note:
        Only shows tracked files, not untracked files.
    """
    completed_process = run_subprocess(["git", "diff"])
    unstaged_changes: str = completed_process.stdout.decode("utf-8")
    return unstaged_changes


def git_add_file(path: Path, *, check: bool = True) -> CompletedProcess[bytes]:
    """Stage a file to the git index.

    Converts absolute paths to relative before staging.

    Args:
        path: File path to stage (absolute or relative).
        check: Whether to raise exception on failure.

    Returns:
        CompletedProcess from subprocess execution.

    Raises:
        subprocess.CalledProcessError: If check=True and command fails.
    """
    # make path relative to cwd if it is absolute
    if path.is_absolute():
        path = path.relative_to(Path.cwd())
    logger.debug("Adding file to git: %s", path)
    return run_subprocess(["git", "add", str(path)], check=check)


def get_repo_url_from_git() -> str:
    """Construct HTTPS GitHub repository URL.

    Returns:
        URL in format: `https://github.com/{owner}/{repo}`
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://github.com/{owner}/{repo}"


def get_github_pages_url_from_git() -> str:
    """Construct GitHub Pages URL.

    Returns:
        URL in format: `https://{owner}.github.io/{repo}`

    Note:
        Site may not exist if GitHub Pages not enabled.
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://{owner}.github.io/{repo}"


def get_codecov_url_from_git() -> str:
    """Construct Codecov dashboard URL.

    Returns:
        URL in format: `https://codecov.io/gh/{owner}/{repo}`
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://codecov.io/gh/{owner}/{repo}"


def get_pypi_url_from_git() -> str:
    """Construct PyPI package URL.

    Assumes package name matches repository name.

    Returns:
        URL in format: `https://pypi.org/project/{repo}`
    """
    _, repo = get_repo_owner_and_name_from_git(check_repo_url=False, url_encode=True)
    return f"https://pypi.org/project/{repo}"


def get_pypi_badge_url_from_git() -> str:
    """Construct PyPI version badge URL.

    Returns:
        shields.io badge URL for PyPI version.
    """
    _, repo = get_repo_owner_and_name_from_git(check_repo_url=False, url_encode=True)
    return f"https://img.shields.io/pypi/v/{repo}?logo=pypi&logoColor=white"


def get_workflow_run_url_from_git(workflow_name: str) -> str:
    """Construct GitHub Actions workflow run URL.

    Args:
        workflow_name: Workflow file name without `.yaml` extension.

    Returns:
        URL to workflow execution history.
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://github.com/{owner}/{repo}/actions/workflows/{workflow_name}.yaml"


def get_workflow_badge_url_from_git(workflow_name: str, label: str, logo: str) -> str:
    """Construct GitHub Actions workflow status badge URL.

    Args:
        workflow_name: Workflow file name without `.yaml` extension.
        label: Badge text label (e.g., "CI", "Build").
        logo: shields.io logo identifier (e.g., "github", "python").

    Returns:
        shields.io badge URL showing workflow status.
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow_name}.yaml?label={label}&logo={logo}"


def get_licence_badge_url_from_git() -> str:
    """Construct GitHub license badge URL.

    Returns:
        shields.io badge URL showing repository license.
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://img.shields.io/github/license/{owner}/{repo}"


def running_in_github_actions() -> bool:
    """Detect if executing inside GitHub Actions workflow.

    Returns:
        True if running in GitHub Actions, False otherwise.

    Note:
        Checks for GITHUB_ACTIONS environment variable.
    """
    return os.getenv("GITHUB_ACTIONS", "false") == "true"
