"""GitHub branch protection ruleset configuration.

Generates branch-protection.json with GitHub ruleset config enforcing PR reviews,
status checks, linear history, signed commits, and protection against force pushes.
Upload via Settings > Rules > Rulesets.

See Also:
    https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets
"""

import logging
from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.json import JsonConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow
from pyrig.dev.management.version_controller import VersionController
from pyrig.dev.utils.github_api import create_or_update_ruleset, get_repo
from pyrig.dev.utils.version_control import get_github_repo_token

logger = logging.getLogger(__name__)


class RepoProtectionConfigFile(JsonConfigFile):
    """Manages branch-protection.json for GitHub rulesets.

    Creates JSON config with PR requirements (1 approval, code owner review),
    status checks (health check workflow), linear history, signed commits,
    and protection rules. Upload to Settings > Rules > Rulesets.

    See Also:
        pyrig.dev.configs.workflows.health_check.HealthCheckWorkflow
        pyrig.dev.utils.version_control.DEFAULT_RULESET_NAME
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get parent directory (project root)."""
        return Path()

    @classmethod
    def get_filename(cls) -> str:
        """Get filename with hyphens (branch-protection)."""
        return "branch-protection"

    @classmethod
    def _get_configs(cls) -> dict[str, Any]:
        """Get GitHub ruleset config.

        Returns:
            Dict with PR requirements, status checks, and protections.
        """
        status_check_id = HealthCheckWorkflow.make_id_from_func(
            HealthCheckWorkflow.job_health_check
        )
        bypass_id = 5  # GitHubs standard id for repo owner
        return {
            "name": VersionController.L.get_default_ruleset_name(),
            "target": "branch",
            "enforcement": "active",
            "conditions": {"ref_name": {"exclude": [], "include": ["~DEFAULT_BRANCH"]}},
            "rules": [
                {"type": "creation"},
                {"type": "update"},
                {"type": "deletion"},
                {"type": "required_linear_history"},
                {"type": "required_signatures"},
                {
                    "type": "pull_request",
                    "parameters": {
                        "required_approving_review_count": 1,
                        "dismiss_stale_reviews_on_push": True,
                        "required_reviewers": [],
                        "require_code_owner_review": True,
                        "require_last_push_approval": True,
                        "required_review_thread_resolution": True,
                        "allowed_merge_methods": ["squash", "rebase"],
                    },
                },
                {
                    "type": "required_status_checks",
                    "parameters": {
                        "strict_required_status_checks_policy": True,
                        "do_not_enforce_on_create": True,
                        "required_status_checks": [{"context": status_check_id}],
                    },
                },
                {"type": "non_fast_forward"},
            ],
            "bypass_actors": [
                {
                    "actor_id": bypass_id,
                    "actor_type": "RepositoryRole",
                    "bypass_mode": "always",
                }
            ],
        }

    @classmethod
    def protect_repo(cls) -> None:
        """Apply security protections to the GitHub repository.

        Configures repository-level settings and branch protection rulesets.
        """
        cls.set_secure_repo_settings()
        cls.create_or_update_default_branch_ruleset()

    @classmethod
    def create_or_update_default_branch_ruleset(cls) -> None:
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
            **cls.load(),
        )

    @classmethod
    def set_secure_repo_settings(cls) -> None:
        """Configure repository-level security and merge settings.

        Sets description, default branch, merge options, and branch cleanup
        settings based on pyproject.toml and pyrig defaults.
        """
        logger.info("Configuring secure repository settings")
        owner, repo_name = VersionController.L.get_repo_owner_and_name()
        token = get_github_repo_token()
        repo = get_repo(token, owner, repo_name)

        toml_description = PyprojectConfigFile.L.get_project_description()
        logger.debug("Setting repository description: %s", toml_description)

        repo.edit(
            name=repo_name,
            description=toml_description,
            default_branch=VersionController.L.get_default_branch(),
            delete_branch_on_merge=True,
            allow_update_branch=True,
            allow_merge_commit=False,
            allow_rebase_merge=True,
            allow_squash_merge=True,
        )
        logger.info("Repository settings configured successfully")
