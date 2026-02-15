"""GitHub Actions workflow for creating releases.

This module provides the ReleaseWorkflowConfigFile class for creating a GitHub Actions
workflow that creates GitHub releases with version tags and changelogs after
successful artifact builds.

The workflow:
    - Updates the project version and creates a git tag (e.g., v1.2.3)
    - Downloads artifacts from the triggering build workflow run
    - Generates changelogs from commit history
    - Publishes GitHub releases with artifacts attached

This enables automated semantic versioning and release management.

See Also:
    pyrig.rig.configs.workflows.build.BuildWorkflowConfigFile
        Must complete successfully before this workflow runs
    pyrig.rig.configs.workflows.deploy.DeployWorkflowConfigFile
        Runs after this workflow to deploy to PyPI and GitHub Pages
"""

from typing import Any

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.workflows.build import BuildWorkflowConfigFile


class ReleaseWorkflowConfigFile(WorkflowConfigFile):
    """GitHub Actions workflow for creating GitHub releases.

    Generates a .github/workflows/release.yml file that creates GitHub releases
    with version tags and changelogs after successful builds.

    The workflow:
        - Triggers after BuildWorkflowConfigFile completes successfully
        - Updates the project version, pushes commits, and creates/pushes a git tag
        - Downloads artifacts (wheels, container images)
          from the triggering build workflow run
        - Generates changelogs from commit history
        - Publishes GitHub releases with artifacts attached
        - Requires write permissions for contents and read for actions

    Release Process:
        1. Checkout and set up the project environment
        2. Update/install dependencies
        3. Bump patch version and stage changes
        4. Run prek, commit changes, and push commits
        5. Create and push a version tag
        6. Download build artifacts from the triggering workflow run
        7. Generate changelog and create the GitHub release

    Example:
        Generate release.yml workflow:

        >>> from pyrig.rig.configs.workflows.release import ReleaseWorkflowConfigFile
        >>> ReleaseWorkflowConfigFile.I.validate()

    See Also:
        pyrig.rig.configs.workflows.build.BuildWorkflowConfigFile
            Triggers this workflow on completion
        pyrig.rig.configs.workflows.deploy.DeployWorkflowConfigFile
            Runs after this workflow completes
        pyrig.rig.configs.pyproject.PyprojectConfigFile
            Provides version information for tagging
    """

    def workflow_triggers(self) -> dict[str, Any]:
        """Get the workflow triggers.

        Returns:
            Trigger for build workflow completion.
        """
        triggers = super().workflow_triggers()
        triggers.update(
            self.on_workflow_run(
                workflows=[BuildWorkflowConfigFile.I.workflow_name()],
            )
        )
        return triggers

    def permissions(self) -> dict[str, Any]:
        """Get the workflow permissions.

        Returns:
            Permissions with write access for creating releases.
        """
        permissions = super().permissions()
        permissions["contents"] = "write"
        permissions["actions"] = "read"
        return permissions

    def jobs(self) -> dict[str, Any]:
        """Get the workflow jobs.

        Returns:
            Dict with release job.
        """
        jobs: dict[str, Any] = {}
        jobs.update(self.job_release())
        return jobs

    def job_release(self) -> dict[str, Any]:
        """Get the release job that creates the GitHub release.

        Returns:
            Job configuration for creating releases.
        """
        return self.job(
            job_func=self.job_release,
            if_condition=self.if_workflow_run_is_success(),
            steps=self.steps_release(),
        )

    def steps_release(self) -> list[dict[str, Any]]:
        """Get the steps for creating the release.

        Returns:
            List of steps for tagging, changelog, and release creation.
        """
        return [
            *self.steps_core_installed_setup(repo_token=True, patch_version=True),
            self.step_commit_added_changes(),
            self.step_push_commits(),
            self.step_create_and_push_tag(),
            self.step_extract_version(),
            self.step_download_artifacts_from_workflow_run(),
            self.step_build_changelog(),
            self.step_create_release(),
        ]
