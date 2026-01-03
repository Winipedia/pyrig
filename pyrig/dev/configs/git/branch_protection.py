"""GitHub branch protection ruleset configuration.

Generates branch-protection.json with GitHub ruleset config enforcing PR reviews,
status checks, linear history, signed commits, and protection against force pushes.
Upload via Settings > Rules > Rulesets.

See Also:
    https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets
"""

from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.json import JsonConfigFile
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow
from pyrig.dev.utils.git import DEFAULT_RULESET_NAME
from pyrig.src.modules.package import get_project_name_from_pkg_name


class BranchProtectionConfigFile(JsonConfigFile):
    """Manages branch-protection.json for GitHub rulesets.

    Creates JSON config with PR requirements (1 approval, code owner review),
    status checks (health check workflow), linear history, signed commits,
    and protection rules. Upload to Settings > Rules > Rulesets.

    See Also:
        pyrig.dev.configs.workflows.health_check.HealthCheckWorkflow
        pyrig.dev.utils.git.DEFAULT_RULESET_NAME
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get parent directory (project root)."""
        return Path()

    @classmethod
    def get_filename(cls) -> str:
        """Get filename with hyphens (branch-protection)."""
        name = super().get_filename()
        return get_project_name_from_pkg_name(name)  # replaces _ with -

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get GitHub ruleset config.

        Returns:
            Dict with PR requirements, status checks, and protections.
        """
        status_check_id = HealthCheckWorkflow.make_id_from_func(
            HealthCheckWorkflow.job_health_check
        )
        bypass_id = 5  # GitHubs standard id for repo owner
        return {
            "name": DEFAULT_RULESET_NAME,
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
