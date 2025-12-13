"""GitHub Actions workflow for creating releases.

This module provides the ReleaseWorkflow class for creating
a workflow that creates tags and publishes GitHub releases
after successful build workflow completion.
"""

from typing import Any

from pyrig.dev.configs.workflows.base.base import Workflow
from pyrig.dev.configs.workflows.build import BuildWorkflow


class ReleaseWorkflow(Workflow):
    """Workflow for creating GitHub releases.

    Triggers after build workflow completes successfully.
    Downloads artifacts from the build workflow, creates version tags,
    generates changelogs, and publishes GitHub releases.
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
            cls.step_run_pre_commit_hooks(),
            cls.step_commit_added_changes(),
            cls.step_push_commits(),
            cls.step_create_and_push_tag(),
            cls.step_extract_version(),
            cls.step_download_artifacts_from_workflow_run(),
            cls.step_build_changelog(),
            cls.step_create_release(),
        ]
