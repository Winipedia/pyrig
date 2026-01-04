"""GitHub repository API utilities and ruleset management.

Utilities for interacting with the GitHub API, specifically for repository rulesets
and gitignore file handling. Uses PyGithub for authentication and API calls.

GitHub rulesets are the modern mechanism for branch protection, offering more
flexibility than legacy branch protection rules.

Functions:
    get_rules_payload: Build a rules array for GitHub rulesets
    create_or_update_ruleset: Create or update a repository ruleset
    get_all_rulesets: Retrieve all rulesets for a repository
    get_repo: Get a PyGithub Repository object
    ruleset_exists: Check if a ruleset with a given name exists
    github_api_request: Make a generic GitHub API request
    get_github_repo_token: Retrieve GitHub token from environment or .env
    path_is_in_gitignore_lines: Check if a path matches gitignore patterns
    load_gitignore: Load gitignore file as a list of patterns

Module Attributes:
    DEFAULT_BRANCH (str): Default branch name ("main")
    DEFAULT_RULESET_NAME (str): Default protection ruleset name
    GITIGNORE_PATH (Path): Path to .gitignore file

Examples:
    Create a ruleset with pull request requirements::

        >>> from pyrig.dev.utils.git import create_or_update_ruleset, get_rules_payload
        >>> rules = get_rules_payload(
        ...     pull_request={"required_approving_review_count": 1},
        ...     deletion={}
        ... )
        >>> create_or_update_ruleset(
        ...     token="ghp_...", owner="myorg", repo_name="myrepo",
        ...     name="main-protection", target="branch",
        ...     enforcement="active", rules=rules
        ... )

See Also:
    pyrig.dev.cli.commands.protect_repo: High-level repository protection
"""

import logging
import os
from pathlib import Path

import pathspec
from dotenv import dotenv_values

logger = logging.getLogger(__name__)

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
