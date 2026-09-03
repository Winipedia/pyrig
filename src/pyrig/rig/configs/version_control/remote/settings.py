"""Repository-level settings and protection ruleset configuration for GitHub."""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.json import JSONDictConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.docs.builder import DocsBuilder
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.controller import VersionController
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class RepositorySettingsConfigFile(JSONDictConfigFile):
    """Configuration file for GitHub repository settings and protection rulesets.

    Manages `.github/settings.json`, containing the general repository settings
    and protection rulesets to apply to the repository.
    """

    def _configs(self) -> dict[str, Any]:
        """Build the required repository settings and protection rulesets.

        The branch ruleset targets the default branch, requires pull request
        review, a passing health-check status check, linear history, and
        signed commits, and blocks branch creation, deletion, and force
        pushes. The tag ruleset targets every tag and blocks deletion and
        retargeting, keeping released versions immutable. Repository admins
        are exempt from both rulesets.

        Returns:
            Dict keyed by `repository_key()` and `rulesets_key()`.
        """
        status_check_id = HealthCheckWorkflowConfigFile.I.name_from_id(
            HealthCheckWorkflowConfigFile.I.job_id_from_method(
                HealthCheckWorkflowConfigFile.I.job_health_check,
            ),
        )
        return {
            self.repository_key(): {
                "name": PackageManager.I.project_name(),
                "description": PyprojectConfigFile.I.project_description(),
                "homepage": DocsBuilder.I.documentation_url(),
                "default_branch": VersionController.I.default_branch(),
                "delete_branch_on_merge": True,
                "allow_update_branch": True,
                "allow_merge_commit": False,
                "allow_rebase_merge": True,
                "allow_squash_merge": True,
            },
            self.rulesets_key(): [
                {
                    "name": VersionController.I.default_branch(),
                    "target": "branch",
                    "enforcement": "active",
                    "conditions": {
                        "ref_name": {"exclude": [], "include": ["~DEFAULT_BRANCH"]},
                    },
                    "rules": [
                        {"type": "creation"},
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
                                "required_status_checks": [
                                    {"context": status_check_id},
                                ],
                            },
                        },
                        {"type": "non_fast_forward"},
                    ],
                    "bypass_actors": self.bypass_actors(),
                },
                {
                    "name": "tags",
                    "target": "tag",
                    "enforcement": "active",
                    "conditions": {
                        "ref_name": {"exclude": [], "include": ["~ALL"]},
                    },
                    "rules": [
                        {"type": "deletion"},
                        {"type": "update"},
                    ],
                    "bypass_actors": self.bypass_actors(),
                },
            ],
        }

    def bypass_actors(self) -> list[dict[str, Any]]:
        """Return the bypass actors.

        Returns:
            Single-entry list identifying GitHub's fixed Admin repository role.
        """
        return [self.admin_bypass_actor()]

    def admin_bypass_actor(self) -> dict[str, Any]:
        """Return the bypass actor dict granting an always-bypass to repository admins.

        5 is GitHub's fixed ID for the Admin repository role.

        Returns:
            Dict identifying GitHub's fixed Admin repository role.
        """
        return {
            "actor_id": 5,
            "actor_type": "RepositoryRole",
            "bypass_mode": "always",
        }

    def parent_path(self) -> Path:
        """Return the `RemoteVersionController`'s config directory."""
        return RemoteVersionController.I.config_dir()

    def stem(self) -> str:
        """Return `"settings"`."""
        return "settings"

    def repository_key(self) -> str:
        """Return `"repository"`, the top-level key for the repo settings."""
        return "repository"

    def rulesets_key(self) -> str:
        """Return `"rulesets"`, the top-level key for the protection rulesets."""
        return "rulesets"
