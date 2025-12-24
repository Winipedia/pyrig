"""Repository protection and security configuration.

This module provides functions to configure secure repository settings and
branch protection rulesets on GitHub. It implements pyrig's opinionated
security defaults, including required reviews, status checks, and merge
restrictions.

The protection rules enforce:
    - Required pull request reviews with code owner approval
    - Required status checks (health check workflow must pass)
    - Linear commit history (no merge commits)
    - Signed commits
    - No force pushes or deletions

Example:
    >>> from pyrig.src.git.github.repo.protect import protect_repository
    >>> protect_repository()  # Applies all protection rules
"""

import logging
from typing import Any

from pyrig.dev.configs.branch_protection import BranchProtectionConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.utils.github import (
    DEFAULT_BRANCH,
    create_or_update_ruleset,
    get_github_repo_token,
    get_repo,
)
from pyrig.src.git import (
    get_repo_owner_and_name_from_git,
)

logger = logging.getLogger(__name__)


def protect_repository() -> None:
    """Apply all security protections to the repository.

    Configures both repository-level settings and branch protection
    rulesets. This is the main entry point for securing a repository.
    """
    logger.info("Protecting repository")
    set_secure_repo_settings()
    create_or_update_default_branch_ruleset()
    logger.info("Repository protection complete")


def set_secure_repo_settings() -> None:
    """Configure repository-level settings for security and consistency.

    Sets the following repository settings:
        - Description from pyproject.toml
        - Default branch to 'main'
        - Delete branches on merge
        - Allow update branch button
        - Disable merge commits (squash and rebase only)
    """
    logger.info("Configuring secure repository settings")
    owner, repo_name = get_repo_owner_and_name_from_git()
    token = get_github_repo_token()
    repo = get_repo(token, owner, repo_name)

    toml_description = PyprojectConfigFile.get_project_description()
    logger.debug("Setting repository description: %s", toml_description)

    repo.edit(
        name=repo_name,
        description=toml_description,
        default_branch=DEFAULT_BRANCH,
        delete_branch_on_merge=True,
        allow_update_branch=True,
        allow_merge_commit=False,
        allow_rebase_merge=True,
        allow_squash_merge=True,
    )
    logger.info("Repository settings configured successfully")


def create_or_update_default_branch_ruleset() -> None:
    """Create or update the default branch protection ruleset.

    Applies pyrig's standard protection rules to the default branch (main).
    If a ruleset with the same name already exists, it is updated.
    """
    token = get_github_repo_token()
    owner, repo_name = get_repo_owner_and_name_from_git()
    create_or_update_ruleset(
        token=token,
        owner=owner,
        repo_name=repo_name,
        **get_default_ruleset_params(),
    )


def get_default_ruleset_params() -> dict[str, Any]:
    """Build the parameter dictionary for the default branch ruleset.

    Constructs the complete ruleset configuration including:
        - Branch targeting (default branch only)
        - Bypass permissions for repository admins
        - All protection rules (reviews, status checks, etc.)

    Returns:
        A dictionary of parameters suitable for `create_or_update_ruleset()`.
    """
    return BranchProtectionConfigFile.load()
