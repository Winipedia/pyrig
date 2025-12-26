"""Configuration management for GitHub branch protection rulesets.

This module provides the BranchProtectionConfigFile class for managing the
branch protection configuration file. This JSON file contains a complete
GitHub branch protection ruleset configuration that can be uploaded to GitHub
to enforce code quality and security standards.

The generated configuration enforces:
    - Required pull request reviews (1 approver, code owner review)
    - Required status checks (health check workflow must pass)
    - Linear history (no merge commits)
    - Signed commits
    - Protection against force pushes and deletions
    - Last push approval requirement

The configuration file can be:
    1. Uploaded to GitHub via the web UI (Settings > Rules > Rulesets)
    2. Applied via GitHub API
    3. Used as a template for custom rulesets

See Also:
    GitHub Rulesets Documentation:
        https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets
"""

from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.json import JsonConfigFile
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow
from pyrig.dev.utils.git import DEFAULT_RULESET_NAME
from pyrig.src.modules.package import get_project_name_from_pkg_name


class BranchProtectionConfigFile(JsonConfigFile):
    """Configuration file manager for GitHub branch protection rulesets.

    Creates a JSON configuration file (branch-protection.json) in the project
    root that defines a complete GitHub branch protection ruleset. This file
    can be uploaded to GitHub to enforce code quality standards on the default
    branch.

    The generated ruleset includes:
        - **Pull Request Requirements**: 1 approving review, code owner review,
          last push approval, stale review dismissal
        - **Status Checks**: Health check workflow must pass
        - **History Requirements**: Linear history, signed commits
        - **Protection Rules**: No force pushes, no deletions, no direct pushes
        - **Bypass Actors**: Repository owners can bypass rules

    Examples:
        Generate the branch protection configuration::

            from pyrig.dev.configs.branch_protection import BranchProtectionConfigFile

            # Creates branch-protection.json
            BranchProtectionConfigFile()

        The generated file can be uploaded to GitHub::

            1. Go to repository Settings > Rules > Rulesets
            2. Click "Import a ruleset"
            3. Upload the branch-protection.json file

    See Also:
        pyrig.dev.configs.workflows.health_check.HealthCheckWorkflow
            The workflow that must pass as a required status check
        pyrig.dev.utils.git.DEFAULT_RULESET_NAME
            The default name for the ruleset
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for branch-protection.json.

        Returns:
            Path: Empty Path() representing the project root directory.
        """
        return Path()

    @classmethod
    def get_filename(cls) -> str:
        """Get the branch protection filename.

        Converts the class name to a hyphenated filename (e.g.,
        BranchProtectionConfigFile -> branch-protection).

        Returns:
            str: The string "branch-protection".

        Note:
            This method converts underscores to hyphens for consistency with
            common naming conventions for configuration files.
        """
        name = super().get_filename()
        # replaces _ with -
        return get_project_name_from_pkg_name(name)

    @classmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the complete branch protection ruleset configuration.

        Generates a GitHub branch protection ruleset configuration that enforces
        code quality and security standards. The configuration matches the format
        that can be downloaded from or uploaded to GitHub's ruleset settings.

        The configuration includes:
            - **Name**: Default ruleset name from DEFAULT_RULESET_NAME
            - **Target**: Applies to branches (specifically the default branch)
            - **Enforcement**: Active (rules are enforced)
            - **Rules**:
                - creation: Prevents branch creation
                - update: Prevents updates except via PR
                - deletion: Prevents branch deletion
                - required_linear_history: No merge commits
                - required_signatures: Commits must be signed
                - pull_request: Requires 1 approval, code owner review, etc.
                - required_status_checks: Health check workflow must pass
                - non_fast_forward: Prevents force pushes
            - **Bypass Actors**: Repository owners can bypass rules

        Returns:
            dict[str, Any]: Complete GitHub ruleset configuration in the format
                expected by GitHub's API and web UI.

        Note:
            The status check ID is derived from the HealthCheckWorkflow class.
            The bypass actor ID (5) is GitHub's standard ID for repository owners.

        Examples:
            The returned configuration can be uploaded to GitHub::

                {
                    "name": "Default",
                    "target": "branch",
                    "enforcement": "active",
                    "conditions": {...},
                    "rules": [...],
                    "bypass_actors": [...]
                }
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
