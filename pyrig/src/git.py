"""Git repository utilities for URL parsing and GitHub integration.

This module provides utilities for extracting repository information from git
configuration and generating GitHub-related URLs. It supports common git
operations like reading remote URLs, extracting owner/repo names, and
constructing URLs for GitHub Pages, PyPI, badges, and workflows.

The utilities are designed to work with local git repositories and derive
repository information from git configuration, enabling automatic generation
of URLs for documentation, badges, and CI/CD workflows.

Key capabilities:
    - **Git config reading**: Extract remote URLs and user information from
      local git configuration
    - **URL parsing**: Parse GitHub owner and repository names from HTTPS and
      SSH remote URLs
    - **URL generation**: Construct URLs for GitHub Pages, PyPI, Codecov,
      badges, and workflow runs
    - **Git operations**: Stage files and check for uncommitted changes
    - **Environment detection**: Detect GitHub Actions CI/CD environment

Example:
    >>> from pyrig.src.git import (
    ...     get_repo_owner_and_name_from_git,
    ...     get_repo_url_from_git
    ... )
    >>> owner, repo = get_repo_owner_and_name_from_git()
    >>> print(f"{owner}/{repo}")
    'myorg/myrepo'
    >>> print(get_repo_url_from_git())
    'https://github.com/myorg/myrepo'

Note:
    This module is part of `pyrig.src` and has minimal dependencies, making it
    suitable for runtime use. For GitHub API operations and token management,
    see `pyrig.dev.utils.git`.

See Also:
    pyrig.dev.utils.git: GitHub API operations and token management
    pyrig.src.os.os.run_subprocess: Subprocess execution used by git commands
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

    Executes `git config --get remote.origin.url` to retrieve the URL of the
    origin remote. The result is cached to avoid repeated subprocess calls.

    The remote URL can be in either HTTPS or SSH format:
        - HTTPS: `https://github.com/owner/repo.git`
        - SSH: `git@github.com:owner/repo.git`

    Args:
        check: Whether to raise an exception if the git command fails. When
            False, allows the function to return empty string if no remote is
            configured.

    Returns:
        The remote origin URL with any trailing whitespace removed. Returns
        empty string if `check=False` and no remote is configured.

    Raises:
        subprocess.CalledProcessError: If `check=True` and the command fails
            (e.g., not in a git repository or origin remote not configured).

    Example:
        >>> url = get_repo_remote_from_git()
        >>> print(url)
        'https://github.com/myorg/myrepo.git'

    Note:
        This function is cached using `functools.cache`, so repeated calls
        return the same result without executing the git command again.

    See Also:
        get_repo_owner_and_name_from_git: Parse owner and repo from the URL
        pyrig.src.os.os.run_subprocess: Subprocess execution wrapper
    """
    stdout: str = run_subprocess(
        ["git", "config", "--get", "remote.origin.url"], check=check
    ).stdout.decode("utf-8")
    return stdout.strip()


@cache
def get_git_username() -> str:
    """Get the git username from the local git configuration.

    Executes `git config --get user.name` to retrieve the configured username.
    The result is cached to avoid repeated subprocess calls.

    This username is typically set during git installation or via:
        `git config --global user.name "Your Name"`

    Returns:
        The configured git username with any trailing whitespace removed.

    Raises:
        subprocess.CalledProcessError: If the git command fails (e.g., not in
            a git repository or user.name not configured).

    Example:
        >>> username = get_git_username()
        >>> print(username)
        'John Doe'

    Note:
        This function is cached using `functools.cache`, so repeated calls
        return the same result without executing the git command again.

    See Also:
        get_repo_owner_and_name_from_git: Uses this as fallback for owner name
        pyrig.src.os.os.run_subprocess: Subprocess execution wrapper
    """
    stdout: str = run_subprocess(["git", "config", "--get", "user.name"]).stdout.decode(
        "utf-8"
    )
    return stdout.strip()


def get_repo_owner_and_name_from_git(
    *, check_repo_url: bool = True, url_encode: bool = False
) -> tuple[str, str]:
    """Extract the GitHub owner and repository name from the git remote URL.

    Parses the remote origin URL to extract the owner (organization or user)
    and repository name. Handles both HTTPS and SSH URL formats:
        - HTTPS: `https://github.com/owner/repo.git` → ("owner", "repo")
        - SSH: `git@github.com:owner/repo.git` → ("owner", "repo")

    If no remote URL is configured, falls back to using the git username and
    current directory name.

    Args:
        check_repo_url: Whether to raise an exception if the git remote cannot
            be read. When False, falls back to username/directory name if no
            remote is configured.
        url_encode: Whether to URL-encode the owner and repository names using
            `urllib.parse.quote`. Useful when constructing URLs that may contain
            special characters.

    Returns:
        A tuple of (owner, repository_name). Both values are URL-encoded if
        `url_encode=True`.

    Raises:
        subprocess.CalledProcessError: If `check_repo_url=True` and the git
            remote cannot be read.

    Example:
        >>> owner, repo = get_repo_owner_and_name_from_git()
        >>> print(f"{owner}/{repo}")
        'myorg/myrepo'

        >>> # With URL encoding for special characters
        >>> owner, repo = get_repo_owner_and_name_from_git(url_encode=True)
        >>> print(f"{owner}/{repo}")
        'my-org/my%2Frepo'  # Forward slash encoded

    Note:
        The fallback behavior (when no remote is configured) uses:
            - Owner: Result of `get_git_username()`
            - Repo: Result of `get_project_name_from_cwd()`

    See Also:
        get_repo_remote_from_git: Retrieves the remote URL
        get_git_username: Fallback for owner name
        pyrig.src.modules.package.get_project_name_from_cwd: Fallback for repo name
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
    """Get the diff of unstaged changes in the git repository.

    Executes `git diff` to retrieve all unstaged changes (modifications to
    tracked files that haven't been staged with `git add`).

    Returns:
        The complete output of `git diff` as a string. Returns empty string
        if there are no unstaged changes.

    Example:
        >>> changes = get_git_unstaged_changes()
        >>> if changes:
        ...     print("Unstaged changes detected")
        ... else:
        ...     print("No unstaged changes")

    Note:
        This only shows changes to tracked files. Untracked files are not
        included in the diff output.

    See Also:
        git_add_file: Stage a file to the git index
        pyrig.src.os.os.run_subprocess: Subprocess execution wrapper
    """
    completed_process = run_subprocess(["git", "diff"])
    unstaged_changes: str = completed_process.stdout.decode("utf-8")
    return unstaged_changes


def git_add_file(path: Path, *, check: bool = True) -> CompletedProcess[bytes]:
    """Stage a file to the git index.

    Executes `git add <path>` to stage the specified file for commit. If the
    path is absolute, it is converted to a relative path from the current
    working directory.

    Args:
        path: Path to the file to stage. Can be absolute or relative. If
            absolute, it will be converted to a path relative to the current
            working directory.
        check: Whether to raise an exception if the git command fails. When
            False, allows the function to complete even if the file cannot
            be staged.

    Returns:
        The CompletedProcess object from the subprocess execution, containing
        return code, stdout, and stderr.

    Raises:
        subprocess.CalledProcessError: If `check=True` and the git command
            fails (e.g., file doesn't exist or not in a git repository).

    Example:
        >>> from pathlib import Path
        >>> git_add_file(Path("src/module.py"))
        CompletedProcess(...)

        >>> # With absolute path
        >>> git_add_file(Path.cwd() / "src" / "module.py")
        CompletedProcess(...)

    Note:
        The path conversion ensures that `git add` receives a relative path,
        which is the standard convention for git commands.

    See Also:
        get_git_unstaged_changes: Check for unstaged changes
        pyrig.src.os.os.run_subprocess: Subprocess execution wrapper
    """
    # make path relative to cwd if it is absolute
    if path.is_absolute():
        path = path.relative_to(Path.cwd())
    logger.debug("Adding file to git: %s", path)
    return run_subprocess(["git", "add", str(path)], check=check)


def get_repo_url_from_git() -> str:
    """Construct the HTTPS GitHub repository URL.

    Generates the browser-accessible GitHub repository URL from the git remote
    configuration. This is the URL you would use in a web browser, not the SSH
    URL used for git operations.

    Returns:
        The HTTPS GitHub repository URL in the format:
        `https://github.com/{owner}/{repo}`

    Example:
        >>> url = get_repo_url_from_git()
        >>> print(url)
        'https://github.com/myorg/myrepo'

    Note:
        Uses `check_repo_url=False` to fall back to username/directory name if
        no git remote is configured. The owner and repo names are URL-encoded
        to handle special characters.

    See Also:
        get_repo_owner_and_name_from_git: Extracts owner and repo names
        get_github_pages_url_from_git: GitHub Pages URL
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://github.com/{owner}/{repo}"


def get_github_pages_url_from_git() -> str:
    """Construct the GitHub Pages URL for the repository.

    Generates the GitHub Pages URL where the repository's documentation site
    is hosted. GitHub Pages URLs follow the pattern `https://{owner}.github.io/{repo}`.

    Returns:
        The GitHub Pages URL in the format:
        `https://{owner}.github.io/{repo}`

    Example:
        >>> url = get_github_pages_url_from_git()
        >>> print(url)
        'https://myorg.github.io/myrepo'

    Note:
        This function generates the URL based on the standard GitHub Pages
        naming convention. The actual site may not exist if GitHub Pages is
        not enabled for the repository.

    See Also:
        get_repo_url_from_git: Main repository URL
        pyrig.dev.configs.pyproject.PyprojectConfigFile: Uses this for docs URL
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://{owner}.github.io/{repo}"


def get_codecov_url_from_git() -> str:
    """Construct the Codecov dashboard URL for the repository.

    Generates the Codecov URL where code coverage reports are displayed.
    Codecov URLs follow the pattern `https://codecov.io/gh/{owner}/{repo}`.

    Returns:
        The Codecov dashboard URL in the format:
        `https://codecov.io/gh/{owner}/{repo}`

    Example:
        >>> url = get_codecov_url_from_git()
        >>> print(url)
        'https://codecov.io/gh/myorg/myrepo'

    Note:
        This function generates the URL based on the standard Codecov naming
        convention. The actual dashboard may not exist if Codecov is not
        configured for the repository.

    See Also:
        get_repo_url_from_git: Main repository URL
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://codecov.io/gh/{owner}/{repo}"


def get_pypi_url_from_git() -> str:
    """Construct the PyPI package URL based on the repository name.

    Generates the PyPI package URL assuming the package name matches the
    repository name. PyPI URLs follow the pattern `https://pypi.org/project/{package}`.

    Returns:
        The PyPI package URL in the format:
        `https://pypi.org/project/{repo}`

    Example:
        >>> url = get_pypi_url_from_git()
        >>> print(url)
        'https://pypi.org/project/myrepo'

    Note:
        This assumes the PyPI package name matches the repository name. The
        actual package may not exist if not published to PyPI.

    See Also:
        get_pypi_badge_url_from_git: PyPI version badge URL
        get_repo_url_from_git: Main repository URL
    """
    _, repo = get_repo_owner_and_name_from_git(check_repo_url=False, url_encode=True)
    return f"https://pypi.org/project/{repo}"


def get_pypi_badge_url_from_git() -> str:
    """Construct the PyPI version badge URL for the repository.

    Generates a shields.io badge URL that displays the latest PyPI version
    for the package. Assumes the package name matches the repository name.

    Returns:
        The PyPI badge URL in the format:
        `https://img.shields.io/pypi/v/{repo}?logo=pypi&logoColor=white`

    Example:
        >>> url = get_pypi_badge_url_from_git()
        >>> print(url)
        'https://img.shields.io/pypi/v/myrepo?logo=pypi&logoColor=white'

    Note:
        The badge will display "not found" if the package is not published to
        PyPI. The badge includes the PyPI logo with white color.

    See Also:
        get_pypi_url_from_git: PyPI package URL
        get_workflow_badge_url_from_git: GitHub Actions workflow badge
        get_licence_badge_url_from_git: License badge
    """
    _, repo = get_repo_owner_and_name_from_git(check_repo_url=False, url_encode=True)
    return f"https://img.shields.io/pypi/v/{repo}?logo=pypi&logoColor=white"


def get_workflow_run_url_from_git(workflow_name: str) -> str:
    """Construct the GitHub Actions workflow run URL.

    Generates the URL for viewing a specific GitHub Actions workflow's runs.
    This is the browser-accessible URL for the workflow's execution history.

    Args:
        workflow_name: The name of the workflow file without the `.yaml`
            extension (e.g., "ci" for "ci.yaml").

    Returns:
        The workflow run URL in the format:
        `https://github.com/{owner}/{repo}/actions/workflows/{workflow_name}.yaml`

    Example:
        >>> url = get_workflow_run_url_from_git("ci")
        >>> print(url)
        'https://github.com/myorg/myrepo/actions/workflows/ci.yaml'

    Note:
        The workflow file must exist in `.github/workflows/{workflow_name}.yaml`
        for the URL to be valid.

    See Also:
        get_workflow_badge_url_from_git: Workflow status badge URL
        get_repo_url_from_git: Main repository URL
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://github.com/{owner}/{repo}/actions/workflows/{workflow_name}.yaml"


def get_workflow_badge_url_from_git(workflow_name: str, label: str, logo: str) -> str:
    """Construct the GitHub Actions workflow status badge URL.

    Generates a shields.io badge URL that displays the current status of a
    GitHub Actions workflow (passing, failing, etc.).

    Args:
        workflow_name: The name of the workflow file without the `.yaml`
            extension (e.g., "ci" for "ci.yaml").
        label: The text label to display on the badge (e.g., "CI", "Build").
        logo: The logo identifier for shields.io (e.g., "github", "python").

    Returns:
        The workflow badge URL in the format:
        `https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow_name}.yaml?label={label}&logo={logo}`

    Example:
        >>> url = get_workflow_badge_url_from_git("ci", "CI", "github")
        >>> print(url)
        'https://img.shields.io/github/actions/workflow/status/myorg/myrepo/ci.yaml?label=CI&logo=github'

    Note:
        The badge will show the status of the most recent workflow run on the
        default branch.

    See Also:
        get_workflow_run_url_from_git: Workflow run history URL
        get_pypi_badge_url_from_git: PyPI version badge
        get_licence_badge_url_from_git: License badge
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://img.shields.io/github/actions/workflow/status/{owner}/{repo}/{workflow_name}.yaml?label={label}&logo={logo}"


def get_licence_badge_url_from_git() -> str:
    """Construct the GitHub license badge URL.

    Generates a shields.io badge URL that displays the repository's license
    type (e.g., MIT, Apache-2.0).

    Returns:
        The license badge URL in the format:
        `https://img.shields.io/github/license/{owner}/{repo}`

    Example:
        >>> url = get_licence_badge_url_from_git()
        >>> print(url)
        'https://img.shields.io/github/license/myorg/myrepo'

    Note:
        The badge will display "unknown" if no LICENSE file is detected in the
        repository. GitHub automatically detects common license formats.

    See Also:
        get_pypi_badge_url_from_git: PyPI version badge
        get_workflow_badge_url_from_git: Workflow status badge
    """
    owner, repo = get_repo_owner_and_name_from_git(
        check_repo_url=False, url_encode=True
    )
    return f"https://img.shields.io/github/license/{owner}/{repo}"


def running_in_github_actions() -> bool:
    """Detect if the code is executing inside a GitHub Actions workflow.

    GitHub Actions automatically sets the `GITHUB_ACTIONS` environment variable
    to "true" in all workflow runs. This function checks for that variable to
    determine the execution environment.

    Returns:
        True if running inside a GitHub Actions workflow, False otherwise
        (including local development and other CI/CD platforms).

    Example:
        >>> if running_in_github_actions():
        ...     print("Running in CI - using environment variables")
        ... else:
        ...     print("Running locally - using .env file")

    Note:
        This is commonly used to conditionally enable CI-specific behavior,
        such as using environment variables instead of .env files for secrets.

    See Also:
        pyrig.dev.utils.git.get_github_repo_token: Uses this for token source
    """
    return os.getenv("GITHUB_ACTIONS", "false") == "true"
