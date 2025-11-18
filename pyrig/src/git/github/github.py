"""GitHub utilities for working with GitHub repositories."""

import os

from pyrig.dev.configs.dot_env import DotEnvConfigFile


def get_github_repo_token() -> str:
    """Get the GitHub token."""
    # try os env first
    token = os.getenv("REPO_TOKEN")
    if token:
        return token

    # try .env next
    dotenv_path = DotEnvConfigFile.get_path()
    if not dotenv_path.exists():
        msg = f"Expected {dotenv_path} to exist"
        raise ValueError(msg)
    dotenv = DotEnvConfigFile.load()
    token = dotenv.get("REPO_TOKEN")
    if token:
        return token

    msg = f"Expected REPO_TOKEN in {dotenv_path}"
    raise ValueError(msg)


def running_in_github_actions() -> bool:
    """Check if we are running in a GitHub action."""
    return os.getenv("GITHUB_ACTIONS", "false") == "true"
