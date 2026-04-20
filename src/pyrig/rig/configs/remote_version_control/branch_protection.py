"""GitHub branch protection ruleset configuration.

Generates branch-protection.json with GitHub ruleset config enforcing PR reviews,
status checks, linear history, signed commits, and protection against force pushes.
Upload via Settings > Rules > Rulesets.

See Also:
    https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets
"""

import logging
import os
from pathlib import Path

from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.json import ListJsonConfigFile
from pyrig.rig.configs.dot_env import DotEnvConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.remote_version_control.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.remote_version_controller import RemoteVersionController
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.github_api import create_or_update_ruleset, repository

logger = logging.getLogger(__name__)


class BranchProtectionConfigFile(ListJsonConfigFile):
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

    def stem(self) -> str:
        """Get filename with hyphens (branch-protection)."""
        return "branch-protection"

    def _configs(self) -> list[ConfigDict]:
        """Get GitHub ruleset config.

        Each item in the list is a ruleset dict with for a branch protection ruleset
        targeting a branch (e.g. main) with PR review, status check,
        and protection rules.

        Returns:
            a List of Dicts with PR requirements, status checks, and protections.
        """
        status_check_id = HealthCheckWorkflowConfigFile.I.make_id_from_func(
            HealthCheckWorkflowConfigFile.I.job_health_check
        )
        return [
            {
                "name": VersionController.I.default_ruleset_name(),
                "target": "branch",
                "enforcement": "active",
                "conditions": {
                    "ref_name": {"exclude": [], "include": ["~DEFAULT_BRANCH"]}
                },
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
                        "actor_id": 5,  # GitHub's standard ID for repository owner
                        "actor_type": "RepositoryRole",
                        "bypass_mode": "always",
                    }
                ],
            }
        ]

    def repo_token(self) -> str:
        """Retrieve the GitHub repository token for API authentication.

        Searches for REPO_TOKEN in order: environment variable, then .env file.

        Returns:
            GitHub API token string.

        Raises:
            ValueError: If REPO_TOKEN not found in environment variables or .env
                file.

        Example:
            >>> token = self.repo_token()

        Note:
            For ruleset management, token needs `repo` scope. Never commit tokens.
            Use environment variables or .env (gitignored).
        """
        # try os env first
        token = os.getenv(RemoteVersionController.I.access_token_key())
        if token is not None:
            logger.debug("Using repository token from environment variable")
            return token

        dotenv = DotEnvConfigFile.I.load()
        token = dotenv.get(RemoteVersionController.I.access_token_key())
        dotenv_path = DotEnvConfigFile.I.path()
        if token is not None:
            logger.debug("Using repository token from %s file", dotenv_path)
            return token

        msg = f"Expected repository token in {dotenv_path} or as env var."
        raise LookupError(msg)

    def protect_repo(self) -> None:
        """Apply security protections to the GitHub repository.

        Configures repository-level settings and branch protection rulesets.
        """
        self.set_secure_repo_settings()
        self.create_or_update_branch_rulesets()

    def create_or_update_branch_rulesets(self) -> None:
        """Create or update branch protection ruleset for the default branch.

        Applies pyrig's standard protection rules to the main branch. Updates
        existing ruleset if present.
        """
        token = self.repo_token()
        owner, repo_name = VersionController.I.repo_owner_and_name()
        rulesets = self.load()
        for ruleset in rulesets:
            create_or_update_ruleset(
                token=token,
                owner=owner,
                repo_name=repo_name,
                **ruleset,
            )

    def set_secure_repo_settings(self) -> None:
        """Configure repository-level security and merge settings.

        Sets description, default branch, merge options, and branch cleanup
        settings based on pyproject.toml and pyrig defaults.
        """
        logger.debug("Configuring secure repository settings")
        owner, repo_name = VersionController.I.repo_owner_and_name()
        token = self.repo_token()
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
