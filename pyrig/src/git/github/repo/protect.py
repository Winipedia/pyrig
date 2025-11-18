"""Script to protect the repo and branches of a repository."""

from typing import Any

from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.git.github.github import get_github_repo_token
from pyrig.src.git.github.repo.repo import (
    DEFAULT_BRANCH,
    DEFAULT_RULESET_NAME,
    create_or_update_ruleset,
    get_repo,
    get_rules_payload,
)


def protect_repository() -> None:
    """Protect the repository."""
    set_secure_repo_settings()
    create_or_update_default_branch_ruleset()


def set_secure_repo_settings() -> None:
    """Set standard settings for the repository."""
    src_pkg_name = PyprojectConfigFile.get_project_name()
    owner = PyprojectConfigFile.get_main_author_name()
    token = get_github_repo_token()
    repo = get_repo(token, owner, src_pkg_name)

    toml_description = PyprojectConfigFile.get_project_description()

    repo.edit(
        name=src_pkg_name,
        description=toml_description,
        default_branch=DEFAULT_BRANCH,
        delete_branch_on_merge=True,
        allow_update_branch=True,
        allow_merge_commit=False,
        allow_rebase_merge=True,
        allow_squash_merge=True,
    )


def create_or_update_default_branch_ruleset() -> None:
    """Add a branch protection rule to the repository."""
    create_or_update_ruleset(
        **get_default_ruleset_params(),
    )


def get_default_ruleset_params() -> dict[str, Any]:
    """Get the default ruleset parameters."""
    from pyrig.dev.configs.workflows.health_check import (  # noqa: PLC0415
        HealthCheckWorkflow,  # avoid circular import
    )

    repo_name = PyprojectConfigFile.get_project_name()
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
        "owner": PyprojectConfigFile.get_main_author_name(),
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
