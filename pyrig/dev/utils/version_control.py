"""Git utilities for repository configuration and gitignore management.

Utilities for GitHub token retrieval, gitignore file handling, and repository
configuration constants.

Functions:
    get_github_repo_token: Retrieve GitHub token from environment or .env
    path_is_in_ignore: Check if a path matches any pattern in .gitignore

Module Attributes:
    DEFAULT_BRANCH (str): Default branch name ("main")
    DEFAULT_RULESET_NAME (str): Default protection ruleset name

See Also:
    pyrig.dev.utils.github_api: GitHub API utilities for rulesets and repos
    pyrig.dev.cli.commands.protect_repo: High-level repository protection
"""

import logging
import os
from pathlib import Path

import pathspec

from pyrig.dev.configs.dot_env import DotEnvConfigFile
from pyrig.dev.management.version_controller import VersionController

logger = logging.getLogger(__name__)


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
        logger.debug("Using repository token from environment variable")
        return token

    dotenv = DotEnvConfigFile.L.load()
    token = dotenv.get("REPO_TOKEN")
    if token:
        logger.debug(
            "Using repository token from %s file", DotEnvConfigFile.L.get_path()
        )
        return token

    msg = f"Expected repository token in {DotEnvConfigFile.L.get_path()} or as env var."
    raise ValueError(msg)


def path_is_in_ignore(path: str | Path) -> bool:
    """Check if a path matches any pattern in a list of gitignore lines.

    Args:
        path: Path to check (string or Path). Absolute paths converted
            to relative. Directories can have optional trailing slash.

    Returns:
        True if path matches any pattern and would be ignored by Git.

    Raises:
        pathspec.PatternError: If gitignore_lines contains malformed patterns.

    See Also:
        VersionController.L.get_loaded_ignore: Load patterns from .gitignore file.
    """
    as_path = Path(path)
    if as_path.is_absolute():
        as_path = as_path.relative_to(Path.cwd())
    is_dir = as_path.suffix == "" or as_path.is_dir() or str(as_path).endswith(os.sep)
    is_dir = is_dir and not as_path.is_file()

    as_posix = as_path.as_posix()
    if is_dir and not as_posix.endswith("/"):
        as_posix += "/"

    spec = pathspec.PathSpec.from_lines(
        "gitignore",
        VersionController.L.get_loaded_ignore(),
    )

    return spec.match_file(as_posix)
