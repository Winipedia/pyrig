"""GitHub Actions workflow for creating releases.

This module provides the ReleaseWorkflow class for creating a GitHub Actions
workflow that creates GitHub releases with version tags and changelogs after
successful artifact builds.

The workflow:
    - Updates the project version and creates a git tag (e.g., v1.2.3)
    - Downloads artifacts from the triggering build workflow run
    - Generates changelogs from commit history
    - Publishes GitHub releases with artifacts attached

This enables automated semantic versioning and release management.

See Also:
    pyrig.dev.configs.workflows.build.BuildWorkflow
        Must complete successfully before this workflow runs
    pyrig.dev.configs.workflows.publish.PublishWorkflow
        Runs after this workflow to publish to PyPI
"""

from typing import Any

from pyrig.dev.configs.base.workflow import Workflow
from pyrig.dev.configs.workflows.build import BuildWorkflow


class ReleaseWorkflow(Workflow):
    """GitHub Actions workflow for creating GitHub releases.

    Generates a .github/workflows/release.yaml file that creates GitHub releases
    with version tags and changelogs after successful builds.

    The workflow:
        - Triggers after BuildWorkflow completes successfully
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
        4. Run pre-commit, commit changes, and push commits
        5. Create and push a version tag
        6. Download build artifacts from the triggering workflow run
        7. Generate changelog and create the GitHub release

    Examples:
        Generate release.yaml workflow::

            from pyrig.dev.configs.workflows.release import ReleaseWorkflow

            # Creates .github/workflows/release.yaml
            ReleaseWorkflow()

    See Also:
        pyrig.dev.configs.workflows.build.BuildWorkflow
            Triggers this workflow on completion
        pyrig.dev.configs.workflows.publish.PublishWorkflow
            Runs after this workflow completes
        pyrig.dev.configs.pyproject.PyprojectConfigFile
            Provides version information for tagging
    """

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Get the workflow triggers.

        Returns:
            Trigger for build workflow completion.
        """
        triggers = super().get_workflow_triggers()
        triggers.update(
            cls.on_workflow_run(
                workflows=[BuildWorkflow.get_workflow_name()],
            )
        )
        return triggers

    @classmethod
    def get_permissions(cls) -> dict[str, Any]:
        """Get the workflow permissions.

        Returns:
            Permissions with write access for creating releases.
        """
        permissions = super().get_permissions()
        permissions["contents"] = "write"
        permissions["actions"] = "read"
        return permissions

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs.

        Returns:
            Dict with release job.
        """
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_release())
        return jobs

    @classmethod
    def job_release(cls) -> dict[str, Any]:
        """Get the release job that creates the GitHub release.

        Returns:
            Job configuration for creating releases.
        """
        return cls.get_job(
            job_func=cls.job_release,
            if_condition=cls.if_workflow_run_is_success(),
            steps=cls.steps_release(),
        )

    @classmethod
    def steps_release(cls) -> list[dict[str, Any]]:
        """Get the steps for creating the release.

        Returns:
            List of steps for tagging, changelog, and release creation.
        """
        return [
            *cls.steps_core_installed_setup(repo_token=True),
            cls.step_patch_version(),
            cls.step_add_version_bump_to_version_control(),
            cls.step_commit_added_changes(),
            cls.step_push_commits(),
            cls.step_create_and_push_tag(),
            cls.step_extract_version(),
            cls.step_download_artifacts_from_workflow_run(),
            cls.step_build_changelog(),
            cls.step_create_release(),
        ]
