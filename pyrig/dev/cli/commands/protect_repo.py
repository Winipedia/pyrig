"""GitHub repository protection and security configuration.

Configures secure repository settings and branch protection rulesets on GitHub,
implementing pyrig's opinionated security defaults.
"""

import logging
from typing import Any

from pyrig.dev.configs.git.branch_protection import BranchProtectionConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.management.version_controller import VersionController
from pyrig.dev.utils.github_api import (
    create_or_update_ruleset,
    get_repo,
)
from pyrig.dev.utils.version_control import (
    DEFAULT_BRANCH,
    get_github_repo_token,
)

logger = logging.getLogger(__name__)


def protect_repository() -> None:
    """Apply security protections to the GitHub repository.

    Configures repository-level settings and branch protection rulesets.
    """
    logger.info("Protecting repository")
    set_secure_repo_settings()
    create_or_update_default_branch_ruleset()
    logger.info("Repository protection complete")


def set_secure_repo_settings() -> None:
    """Configure repository-level security and merge settings.

    Sets description, default branch, merge options, and branch cleanup
    settings based on pyproject.toml and pyrig defaults.
    """
    logger.info("Configuring secure repository settings")
    owner, repo_name = VersionController.L.get_repo_owner_and_name()
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
    """Create or update branch protection ruleset for the default branch.

    Applies pyrig's standard protection rules to the main branch. Updates
    existing ruleset if present.
    """
    token = get_github_repo_token()
    owner, repo_name = VersionController.L.get_repo_owner_and_name()
    create_or_update_ruleset(
        token=token,
        owner=owner,
        repo_name=repo_name,
        **get_default_ruleset_params(),
    )


def get_default_ruleset_params() -> dict[str, Any]:
    """Load branch protection ruleset parameters from configuration.

    Returns:
        Dictionary of parameters for `create_or_update_ruleset()`.
    """
    return BranchProtectionConfigFile.load()
