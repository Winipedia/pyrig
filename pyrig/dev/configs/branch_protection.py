"""Configuration management for branch protection rulesets.

This module provides the BranchProtectionConfigFile class for managing
the branch protection configuration file. This file can be used to
create or update the default branch protection ruleset on GitHub.
"""

from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.json import JsonConfigFile
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow
from pyrig.dev.utils.git import DEFAULT_RULESET_NAME
from pyrig.src.modules.package import get_project_name_from_pkg_name


class BranchProtectionConfigFile(JsonConfigFile):
    """Configuration file manager for branch protection.

    Creates a branch protection configuration file that can be used to
    create or update the default branch protection ruleset.
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the project root directory.

        Returns:
            Path to the project root.
        """
        return Path()

    @classmethod
    def get_filename(cls) -> str:
        """Get the branch protection filename.

        Returns:
            The string "branch-protection".
        """
        name = super().get_filename()
        # replaces _ with -
        return get_project_name_from_pkg_name(name)

    @classmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the branch protection configuration.

        This is the same as a template you can download from github
        and upload there in the settings as rulesets

        Returns:
            Dict with the branch protection configuration.
        """
        status_check_id = HealthCheckWorkflow.make_id_from_func(
            HealthCheckWorkflow.job_protect_repository
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
