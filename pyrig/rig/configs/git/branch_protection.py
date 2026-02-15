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

from pyrig.rig.configs.base.json import JsonConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.workflows.health_check import HealthCheckWorkflowConfigFile
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.github_api import create_or_update_ruleset, repository
from pyrig.rig.utils.version_control import github_repo_token

logger = logging.getLogger(__name__)


class RepoProtectionConfigFile(JsonConfigFile):
    """Manages branch-protection.json for GitHub rulesets.

    Creates JSON config with PR requirements (1 approval, code owner review),
    status checks (health check workflow), linear history, signed commits,
    and protection rules. Upload to Settings > Rules > Rulesets.

    See Also:
        pyrig.rig.configs.workflows.health_check.HealthCheckWorkflowConfigFile
        pyrig.rig.tools.version_controller.VersionController.default_ruleset_name
    """

    def parent_path(self) -> Path:
        """Get parent directory (project root)."""
        return Path()

    def filename(self) -> str:
        """Get filename with hyphens (branch-protection)."""
        return "branch-protection"

    def _configs(self) -> dict[str, Any]:
        """Get GitHub ruleset config.

        Returns:
            Dict with PR requirements, status checks, and protections.
        """
        status_check_id = HealthCheckWorkflowConfigFile.I.make_id_from_func(
            HealthCheckWorkflowConfigFile.I.job_health_check
        )
        bypass_id = 5  # GitHubs standard id for repo owner
        return {
            "name": VersionController.I.default_ruleset_name(),
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

    def protect_repo(self) -> None:
        """Apply security protections to the GitHub repository.

        Configures repository-level settings and branch protection rulesets.
        """
        self.set_secure_repo_settings()
        self.create_or_update_default_branch_ruleset()

    def create_or_update_default_branch_ruleset(self) -> None:
        """Create or update branch protection ruleset for the default branch.

        Applies pyrig's standard protection rules to the main branch. Updates
        existing ruleset if present.
        """
        token = github_repo_token()
        owner, repo_name = VersionController.I.repo_owner_and_name()
        create_or_update_ruleset(
            token=token,
            owner=owner,
            repo_name=repo_name,
            **self.load(),
        )

    def set_secure_repo_settings(self) -> None:
        """Configure repository-level security and merge settings.

        Sets description, default branch, merge options, and branch cleanup
        settings based on pyproject.toml and pyrig defaults.
        """
        logger.info("Configuring secure repository settings")
        owner, repo_name = VersionController.I.repo_owner_and_name()
        token = github_repo_token()
        repo = repository(token, owner, repo_name)

        toml_description = PyprojectConfigFile.I.project_description()
        logger.debug("Setting repository description: %s", toml_description)

        repo.edit(
            name=repo_name,
            description=toml_description,
            default_branch=VersionController.I.default_branch(),
            delete_branch_on_merge=True,
            allow_update_branch=True,
            allow_merge_commit=False,
            allow_rebase_merge=True,
            allow_squash_merge=True,
        )
        logger.info("Repository settings configured successfully")
