"""GitHub Actions runtime environment detection.

Provides a utility function to detect if code is executing within a GitHub Actions
workflow, enabling environment-aware behavior in CI/CD pipelines.

See Also:
    pyrig.dev.management.version_controller: Git command wrappers and repo info
    pyrig.dev.management.remote_version_controller: GitHub URL construction
"""

import logging
import os

logger = logging.getLogger(__name__)


def running_in_github_actions() -> bool:
    """Detect if code is executing inside a GitHub Actions workflow.

    Used to conditionally enable or disable behavior based on the runtime environment.
    Common use cases include skipping interactive prompts, adjusting logging levels,
    or enabling CI-specific test fixtures.

    Returns:
        True if running in GitHub Actions, False otherwise.

    Example:
        >>> if running_in_github_actions():
        ...     print("Running in CI - skipping interactive prompt")

    Note:
        Detection relies on the `GITHUB_ACTIONS` environment variable, which GitHub
        automatically sets to "true" in all workflow runs.
    """
    return os.getenv("GITHUB_ACTIONS", "false") == "true"
