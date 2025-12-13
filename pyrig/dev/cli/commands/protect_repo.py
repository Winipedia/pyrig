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

from typing import Any

from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.utils.git import (
    DEFAULT_BRANCH,
    DEFAULT_RULESET_NAME,
    create_or_update_ruleset,
    get_github_repo_token,
    get_repo,
    get_rules_payload,
)
from pyrig.src.git.git import (
    get_repo_owner_and_name_from_git,
)


def protect_repository() -> None:
    """Apply all security protections to the repository.

    Configures both repository-level settings and branch protection
    rulesets. This is the main entry point for securing a repository.
    """
    set_secure_repo_settings()
    create_or_update_default_branch_ruleset()


def set_secure_repo_settings() -> None:
    """Configure repository-level settings for security and consistency.

    Sets the following repository settings:
        - Description from pyproject.toml
        - Default branch to 'main'
        - Delete branches on merge
        - Allow update branch button
        - Disable merge commits (squash and rebase only)
    """
    owner, repo_name = get_repo_owner_and_name_from_git()
    token = get_github_repo_token()
    repo = get_repo(token, owner, repo_name)

    toml_description = PyprojectConfigFile.get_project_description()

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


def create_or_update_default_branch_ruleset() -> None:
    """Create or update the default branch protection ruleset.

    Applies pyrig's standard protection rules to the default branch (main).
    If a ruleset with the same name already exists, it is updated.
    """
    create_or_update_ruleset(
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
    from pyrig.dev.configs.workflows.health_check import (  # noqa: PLC0415
        HealthCheckWorkflow,  # avoid circular import
    )

    owner, repo_name = get_repo_owner_and_name_from_git()
    token = get_github_repo_token()

    rules = get_rules_payload(
        deletion={},
        non_fast_forward={},
        creation={},
        update={},
        pull_request={
            "required_approving_review_count": 1,
            "dismiss_stale_reviews_on_push": True,
            "require_code_owner_review": True,
            "require_last_push_approval": True,
            "required_review_thread_resolution": True,
            "allowed_merge_methods": ["squash", "rebase"],
        },
        required_linear_history={},
        required_signatures={},
        required_status_checks={
            "strict_required_status_checks_policy": True,
            "do_not_enforce_on_create": False,
            "required_status_checks": [
                {
                    "context": HealthCheckWorkflow.get_filename(),
                }
            ],
        },
    )

    return {
        "owner": owner,
        "token": token,
        "repo_name": repo_name,
        "ruleset_name": DEFAULT_RULESET_NAME,
        "enforcement": "active",
        "bypass_actors": [
            {
                "actor_id": 5,
                "actor_type": "RepositoryRole",
                "bypass_mode": "always",
            }
        ],
        "target": "branch",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": rules,
    }
