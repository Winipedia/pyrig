"""Git utilities for repository configuration and gitignore management.

Utilities for GitHub token retrieval and gitignore file handling.

Functions:
    github_repo_token: Retrieve GitHub token from environment or .env.
    path_is_in_ignore: Check if a path matches any pattern in .gitignore.

See Also:
    pyrig.rig.utils.github_api: GitHub API utilities for rulesets and repos.
    pyrig.rig.cli.commands.protect_repo: High-level repository protection.
"""

import logging
import os
from pathlib import Path

import pathspec

from pyrig.rig.configs.dot_env import DotEnvConfigFile
from pyrig.rig.tools.version_controller import VersionController

logger = logging.getLogger(__name__)


def github_repo_token() -> str:
    """Retrieve the GitHub repository token for API authentication.

    Searches for REPO_TOKEN in order: environment variable, then .env file.

    Returns:
        GitHub API token string.

    Raises:
        ValueError: If REPO_TOKEN not found in environment variables or .env
            file.

    Example:
        >>> token = github_repo_token()

    Note:
        For ruleset management, token needs `repo` scope. Never commit tokens.
        Use environment variables or .env (gitignored).
    """
    # try os env first
    token = os.getenv("REPO_TOKEN")
    if token:
        logger.debug("Using repository token from environment variable")
        return token

    dotenv = DotEnvConfigFile.I.load()
    token = dotenv.get("REPO_TOKEN")
    if token:
        logger.debug("Using repository token from %s file", DotEnvConfigFile.I.path())
        return token

    msg = f"Expected repository token in {DotEnvConfigFile.I.path()} or as env var."
    raise ValueError(msg)


def path_is_in_ignore(path: str | Path) -> bool:
    """Check if a path matches any pattern in the .gitignore file.

    Args:
        path: Path to check (string or Path). Absolute paths are converted
            to relative. Directories can have an optional trailing slash.

    Returns:
        True if path matches any pattern and would be ignored by Git.

    Raises:
        pathspec.PatternError: If .gitignore contains malformed patterns.

    Examples:
        Check if a directory is ignored:

            >>> path_is_in_ignore("build/")
            True

    See Also:
        VersionController.I.loaded_ignore: Load patterns from .gitignore file.
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
        VersionController.I.loaded_ignore(),
    )

    return spec.match_file(as_posix)
