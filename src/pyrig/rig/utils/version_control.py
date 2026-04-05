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

from pyrig.rig.configs.dot_env import DotEnvConfigFile

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
