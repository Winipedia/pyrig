"""GitHub Actions workflow for creating releases.

This module provides the ReleaseWorkflow class for creating
a workflow that builds artifacts, creates tags, and publishes
GitHub releases after successful health checks.
"""

from typing import Any

from pyrig.dev.builders.base.base import Builder
from pyrig.dev.configs.workflows.base.base import Workflow
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow


class ReleaseWorkflow(Workflow):
    """Workflow for creating GitHub releases.

    Triggers after health check workflow completes on main branch.
    Builds artifacts across OS matrix, creates version tags,
    generates changelogs, and publishes GitHub releases.
    """

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Get the workflow triggers.

        Returns:
            Trigger for health check completion on main.
        """
        triggers = super().get_workflow_triggers()
        triggers.update(
            cls.on_workflow_run(
                workflows=[HealthCheckWorkflow.get_workflow_name()],
                branches=["main"],
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
        return permissions

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs.

        Returns:
            Dict with build and release jobs.
        """
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_build())
        jobs.update(cls.job_release())
        return jobs

    @classmethod
    def job_build(cls) -> dict[str, Any]:
        """Get the build job that runs across OS matrix.

        Returns:
            Job configuration for building artifacts.
        """
        return cls.get_job(
            job_func=cls.job_build,
            if_condition=cls.if_workflow_run_is_success(),
            strategy=cls.strategy_matrix_os(),
            runs_on=cls.insert_matrix_os(),
            steps=cls.steps_build(),
        )

    @classmethod
    def job_release(cls) -> dict[str, Any]:
        """Get the release job that creates the GitHub release.

        Returns:
            Job configuration for creating releases.
        """
        return cls.get_job(
            job_func=cls.job_release,
            needs=[cls.make_id_from_func(cls.job_build)],
            steps=cls.steps_release(),
        )

    @classmethod
    def steps_build(cls) -> list[dict[str, Any]]:
        """Get the steps for building artifacts.

        Returns:
            List of build steps, or placeholder if no builders defined.
        """
        non_abstract_builders = Builder.get_non_abstract_subclasses()
        if not non_abstract_builders:
            return [cls.step_no_builder_defined()]
        return [
            *cls.steps_core_matrix_setup(),
            cls.step_build_artifacts(),
            cls.step_upload_artifacts(),
        ]

    @classmethod
    def steps_release(cls) -> list[dict[str, Any]]:
        """Get the steps for creating the release.

        Returns:
            List of steps for tagging, changelog, and release creation.
        """
        return [
            *cls.steps_core_installed_setup(repo_token=True),
            cls.step_setup_git(),
            cls.step_run_pre_commit_hooks(),
            cls.step_commit_added_changes(),
            cls.step_push_commits(),
            cls.step_create_and_push_tag(),
            cls.step_extract_version(),
            cls.step_download_artifacts(),
            cls.step_build_changelog(),
            cls.step_create_release(),
        ]
