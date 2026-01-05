"""Git repository utilities for URL parsing and GitHub integration.

Provides utilities for extracting repository information from git config and generating
GitHub-related URLs (Pages, PyPI, badges, workflows).
"""

import logging
import os

logger = logging.getLogger(__name__)


def running_in_github_actions() -> bool:
    """Detect if executing inside GitHub Actions workflow.

    Returns:
        True if running in GitHub Actions, False otherwise.

    Note:
        Checks for GITHUB_ACTIONS environment variable.
    """
    return os.getenv("GITHUB_ACTIONS", "false") == "true"
