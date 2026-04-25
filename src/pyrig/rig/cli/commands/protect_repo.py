"""CLI command module for the ``pyrig protect-repo`` subcommand.

Provides the thin adapter function that the CLI invokes to apply security
protections to a GitHub repository. All logic lives in the configuration layer.
"""

from pyrig.rig.configs.remote_version_control.branch_protection import (
    BranchProtectionConfigFile,
)


def protect_repository() -> None:
    """Apply security protections to the GitHub repository.

    This is the CLI entry point for ``pyrig protect-repo``. It delegates entirely
    to ``BranchProtectionConfigFile.I.protect_repo``, which applies two categories
    of protections:

    - **Repository settings**: description, default branch, delete-on-merge,
      and merge method restrictions (squash and rebase only).
    - **Branch protection rulesets**: PR review requirements, required status
      checks (health check workflow), linear history, signed commits, and
      protection against force pushes and branch deletion.

    Requires a GitHub API token with ``repo`` scope, resolved from the
    ``REPO_TOKEN`` environment variable or the project's ``.env`` file.

    Raises:
        LookupError: If ``REPO_TOKEN`` is not found in the environment or
            ``.env`` file.
    """
    BranchProtectionConfigFile.I.protect_repo()
