"""Branch protection ruleset configuration for GitHub repositories.

Manages the generation of branch protection rulesets and
repository-level security settings for use with the GitHub API.
"""

import logging
from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.json import JSONDictConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.version_control.version_controller import VersionController

logger = logging.getLogger(__name__)


class RepoSettingsConfigFile(JSONDictConfigFile):
    """Configuration file for GitHub repository settings and branch protection rulesets.

    Generates and manages ``.github/settings.json``, which contains two top-level
    keys: ``repository`` (general repo settings) and ``rulesets`` (branch protection
    rules). The ruleset targets the default branch and enforces pull request reviews,
    status checks against the health-check workflow, linear commit history, signed
    commits, and protection against force pushes.

    The generated file is applied automatically during the release workflow via the
    GitHub CLI (``gh api``), or can be uploaded manually via the repository's
    Settings > Rules > Rulesets page.
    """

    def parent_path(self) -> Path:
        """Return the directory that will contain the settings.json file.

        Returns:
            ``Path(".github")``, the standard GitHub configuration directory.
        """
        return Path(".github")

    def stem(self) -> str:
        """Return the filename stem for the repository settings configuration file.

        Returns:
            ``'settings'``
        """
        return "settings"

    def _configs(self) -> dict[str, Any]:
        """Build the combined repository settings and ruleset configuration.

        Returns a dict with two keys: ``repository`` (general settings applied
        via ``PATCH /repos/{owner}/{repo}``) and ``rulesets`` (a list of ruleset
        dicts, each matching the shape exported from GitHub's ruleset UI). The
        default ruleset targets the default branch and enables the recommended
        protections for a Python project.

        Returns:
            Dict with ``repository`` and ``rulesets`` keys, ready to be
            serialized as ``.github/settings.json``.
        """
        status_check_id = HealthCheckWorkflowConfigFile.I.make_id_from_func(
            HealthCheckWorkflowConfigFile.I.job_health_check
        )
        return {
            self.repository_key(): {
                "name": PackageManager.I.project_name(),
                "description": PyprojectConfigFile.I.project_description(),
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
                        "ref_name": {"exclude": [], "include": ["~DEFAULT_BRANCH"]}
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
                                "do_not_enforce_on_create": True,
                                "required_status_checks": [
                                    {"context": status_check_id}
                                ],
                            },
                        },
                        {"type": "non_fast_forward"},
                    ],
                    "bypass_actors": [
                        {
                            # 5 is GitHub's fixed ID for the Admin repository role
                            "actor_id": 5,
                            "actor_type": "RepositoryRole",
                            "bypass_mode": "always",
                        }
                    ],
                }
            ],
        }

    def repository_key(self) -> str:
        """Get the key for the repo settings."""
        return "repository"

    def rulesets_key(self) -> str:
        """Get the key for the rulesets."""
        return "rulesets"
