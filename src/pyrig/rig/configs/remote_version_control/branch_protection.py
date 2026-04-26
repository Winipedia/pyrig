"""Branch protection ruleset configuration for GitHub repositories.

Manages the generation and application of branch protection rulesets,
as well as repository-level security settings via the GitHub API.
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
    """Configuration file for GitHub branch protection rulesets.

    Generates and manages ``branch-protection.json``, which defines a GitHub
    repository ruleset targeting the default branch. The ruleset enforces pull
    request reviews, status checks against the health-check workflow, linear
    commit history, signed commits, and protection against force pushes and
    direct updates to the branch.

    The generated file can be applied automatically via the GitHub API using
    ``protect_repo()``, or uploaded manually via the repository's
    Settings > Rules > Rulesets page.
    """

    def parent_path(self) -> Path:
        """Return the directory that will contain the branch-protection.json file.

        Returns:
            An empty ``Path()``, which resolves to the current working directory
            (the project root).
        """
        return Path()

    def stem(self) -> str:
        """Return the filename stem for the branch protection configuration file.

        Returns:
            ``'branch-protection'``
        """
        return "branch-protection"

    def _configs(self) -> list[ConfigDict]:
        """Build the GitHub ruleset configuration for the default branch.

        Constructs a single-element list containing a complete GitHub ruleset
        dict that targets the repository default branch (``~DEFAULT_BRANCH``)
        and enforces the following rules:

        - ``creation``, ``update``, ``deletion``: Restrict who can create,
          update, or delete the protected branch.
        - ``required_linear_history``: Enforces a linear commit history,
          preventing merge commits directly to the branch.
        - ``required_signatures``: Requires all commits to be GPG-signed.
        - ``pull_request``: Requires 1 approving review with code owner review,
          stale review dismissal on push, last-push approval, and resolved
          discussion threads. Only squash and rebase merges are permitted.
        - ``required_status_checks``: Requires the health-check workflow job
          to pass before a pull request can be merged. The branch must also be
          up to date before merging (``strict_required_status_checks_policy``).
        - ``non_fast_forward``: Prevents force-pushes to the branch.

        The repository owner (bypass actor ID 5) is granted unconditional bypass
        rights so that emergency changes can still be applied when necessary.

        Returns:
            A single-element list containing the complete ruleset configuration
            dict, ready to be serialized as ``branch-protection.json``.
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

    def protect_repo(self) -> None:
        """Apply all security protections to the GitHub repository.

        Orchestrates the full repository protection sequence by calling
        ``set_secure_repo_settings()`` to update repository-level settings,
        then ``create_or_update_branch_rulesets()`` to push the branch
        protection ruleset to GitHub.
        """
        self.set_secure_repo_settings()
        self.create_or_update_branch_rulesets()

    def set_secure_repo_settings(self) -> None:
        """Apply repository-level settings via the GitHub API.

        Reads the project description from ``pyproject.toml`` and edits the
        GitHub repository to enforce pyrig's standard configuration:

        - Sets the repository name and description from ``pyproject.toml``.
        - Sets the default branch to ``main``.
        - Enables automatic branch deletion after merging and allows branch
          updates via the GitHub UI.
        - Disables merge commits; enables squash and rebase merges only.
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

    def create_or_update_branch_rulesets(self) -> None:
        """Push the branch protection rulesets from configuration to GitHub.

        Loads the rulesets from ``branch-protection.json`` and creates or
        updates each one on the remote repository. An existing ruleset matching
        by name is updated in place; a ruleset that does not yet exist is
        created as a new one.
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

    def repo_token(self) -> str:
        """Retrieve the GitHub repository token for API authentication.

        Looks up the ``REPO_TOKEN`` environment variable first; if absent,
        reads the value from the project's ``.env`` file.

        Returns:
            The GitHub personal access token string.

        Raises:
            LookupError: If ``REPO_TOKEN`` is not set as an environment variable
                and is not present in the ``.env`` file.

        Note:
            The token must have ``repo`` scope (or ``administration:write``) for
            ruleset management. Never commit tokens — use environment variables
            or a gitignored ``.env`` file.
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
