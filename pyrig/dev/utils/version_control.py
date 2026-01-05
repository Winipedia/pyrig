"""Git utilities for repository configuration and gitignore management.

Utilities for GitHub token retrieval, gitignore file handling, and repository
configuration constants.

Functions:
    get_github_repo_token: Retrieve GitHub token from environment or .env
    path_is_in_gitignore_lines: Check if a path matches gitignore patterns
    load_gitignore: Load gitignore file as a list of patterns

Module Attributes:
    DEFAULT_BRANCH (str): Default branch name ("main")
    DEFAULT_RULESET_NAME (str): Default protection ruleset name
    GITIGNORE_PATH (Path): Path to .gitignore file

See Also:
    pyrig.dev.utils.github: GitHub API utilities for rulesets and repository operations
    pyrig.dev.cli.commands.protect_repo: High-level repository protection
"""

import os
from functools import cache
from pathlib import Path
from urllib.parse import quote

import pathspec
from dotenv import dotenv_values

from pyrig.dev.management.version_controller import VersionController
from pyrig.src.git import logger
from pyrig.src.modules.package import get_project_name_from_cwd

DEFAULT_BRANCH = "main"

DEFAULT_RULESET_NAME = f"{DEFAULT_BRANCH}-protection"

GITIGNORE_PATH = Path(".gitignore")


def get_github_repo_token() -> str:
    """Retrieve the GitHub repository token for API authentication.

    Searches for REPO_TOKEN in order: environment variable, then .env file.

    Returns:
        GitHub API token string.

    Raises:
        ValueError: If .env doesn't exist when REPO_TOKEN not in environment,
            or if REPO_TOKEN not found in .env.

    Examples:
        Get the token::

            >>> token = get_github_repo_token()
            >>> print(token[:7])
            'ghp_...'

    Note:
        For ruleset management, token needs `repo` scope.

    Security:
        Never commit tokens. Use environment variables or .env (gitignored).
    """
    # try os env first
    token = os.getenv("REPO_TOKEN")
    if token:
        logger.debug("Using REPO_TOKEN from environment variable")
        return token

    # try .env next
    dotenv_path = Path(".env")
    if not dotenv_path.exists():
        msg = f"Expected {dotenv_path} to exist"
        raise ValueError(msg)
    dotenv = dotenv_values(dotenv_path)
    token = dotenv.get("REPO_TOKEN")
    if token:
        logger.debug("Using REPO_TOKEN from .env file")
        return token

    msg = f"Expected REPO_TOKEN in {dotenv_path}"
    raise ValueError(msg)


def path_is_in_gitignore_lines(
    gitignore_lines: list[str], relative_path: str | Path
) -> bool:
    """Check if a path matches any pattern in a list of gitignore lines.

    Args:
        gitignore_lines: List of gitignore pattern strings.
        relative_path: Path to check (string or Path). Absolute paths converted
            to relative. Directories can have optional trailing slash.

    Returns:
        True if path matches any pattern and would be ignored by Git.

    Raises:
        pathspec.PatternError: If gitignore_lines contains malformed patterns.

    See Also:
        load_gitignore: Load patterns from .gitignore file.
    """
    as_path = Path(relative_path)
    if as_path.is_absolute():
        as_path = as_path.relative_to(Path.cwd())
    is_dir = (
        bool(as_path.suffix == "") or as_path.is_dir() or str(as_path).endswith(os.sep)
    )
    is_dir = is_dir and not as_path.is_file()

    as_posix = as_path.as_posix()
    if is_dir and not as_posix.endswith("/"):
        as_posix += "/"

    spec = pathspec.PathSpec.from_lines(
        "gitwildmatch",
        gitignore_lines,
    )

    return spec.match_file(as_posix)


def load_gitignore(path: Path = GITIGNORE_PATH) -> list[str]:
    """Load a gitignore file as a list of pattern strings.

    Reads gitignore file and splits into lines. Preserves empty lines and comments
    for use with pathspec.PathSpec.

    Args:
        path: Path to gitignore file. Defaults to GITIGNORE_PATH (".gitignore").

    Returns:
        List of strings, one per line. Includes empty lines and comments.

    Raises:
        FileNotFoundError: If gitignore file doesn't exist.
        UnicodeDecodeError: If file contains invalid UTF-8.

    Examples:
        Load the default .gitignore::

            >>> patterns = load_gitignore()  # doctest: +SKIP
            >>> "__pycache__/" in patterns
            True

    See Also:
        path_is_in_gitignore_lines: Check if path matches patterns

    Note:
        Does not filter or process patterns. Pattern interpretation handled by
        pathspec library.
    """
    return path.read_text(encoding="utf-8").splitlines()


@cache
def get_repo_remote_from_version_control(*, check: bool = True) -> str:
    """Get the remote origin URL from git config.

    Args:
        check: Whether to raise exception if command fails.

    Returns:
        Remote origin URL (HTTPS or SSH format).
        Empty string if check=False and no remote.

    Raises:
        subprocess.CalledProcessError: If check=True and command fails.
    """
    stdout: str = (
        VersionController.L.get_config_get_remote_origin_url_args()
        .run(check=check)
        .stdout.decode("utf-8")
    )
    return stdout.strip()


@cache
def get_username_from_version_control() -> str:
    """Get git username from local config.

    Returns:
        Configured git username (cached).

    Raises:
        subprocess.CalledProcessError: If user.name not configured.
    """
    stdout: str = (
        VersionController.L.get_config_get_user_name_args().run().stdout.decode("utf-8")
    )
    return stdout.strip()


@cache
def get_repo_owner_and_name_from_version_control(
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
    url = get_repo_remote_from_version_control(check=check_repo_url)
    if not url:
        # we default to git username and repo name from cwd
        logger.debug("No git remote found, using git username and CWD for repo info")
        owner = get_username_from_version_control()
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


def get_diff_from_version_control() -> str:
    """Get diff of unstaged changes.

    Returns:
        Output of `git diff` (empty string if no changes).

    Note:
        Only shows tracked files, not untracked files.
    """
    completed_process = VersionController.L.get_diff_args().run()
    unstaged_changes: str = completed_process.stdout.decode("utf-8")
    return unstaged_changes
