"""Contains the release workflow.

This workflow is used to create a release on GitHub.
"""

from typing import Any

from pyrig.dev.artifacts.builder.base.base import Builder
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow


class ReleaseWorkflow(HealthCheckWorkflow):
    """Release workflow.

    This workflow is triggered by a push to the main branch.
    It creates a tag for the release and builds a changelog.
    With tag and changelog it creates a release on GitHub
    """

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Get the workflow triggers."""
        triggers = super().get_workflow_triggers()
        triggers.update(cls.on_push())
        triggers.update(cls.on_schedule(cron="0 6 * * 2"))
        return triggers

    @classmethod
    def get_permissions(cls) -> dict[str, Any]:
        """Get the workflow permissions."""
        permissions = super().get_permissions()
        permissions["contents"] = "write"
        return permissions

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs."""
        jobs = super().get_jobs()
        last_job_name = list(jobs.keys())[-1]
        jobs.update(cls.job_build(needs=[last_job_name]))
        jobs.update(cls.job_release())
        return jobs

    @classmethod
    def job_build(cls, needs: list[str] | None = None) -> dict[str, Any]:
        """Get the build job."""
        return cls.get_job(
            job_func=cls.job_build,
            needs=needs,
            strategy=cls.strategy_matrix_os(),
            runs_on=cls.insert_matrix_os(),
            steps=cls.steps_build(),
        )

    @classmethod
    def job_release(cls) -> dict[str, Any]:
        """Get the release job."""
        return cls.get_job(
            job_func=cls.job_release,
            needs=[cls.make_id_from_func(cls.job_build)],
            steps=cls.steps_release(),
        )

    @classmethod
    def steps_build(cls) -> list[dict[str, Any]]:
        """Get the build steps."""
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
        """Get the release steps."""
        return [
            *cls.steps_core_installed_setup(repo_token=True),
            cls.step_setup_git(),
            cls.step_add_version_patch(),
            cls.step_run_pre_commit_hooks(),
            cls.step_commit_added_changes(),
            cls.step_push_commits(),
            cls.step_create_and_push_tag(),
            cls.step_extract_version(),
            cls.step_download_artifacts(),
            cls.step_build_changelog(),
            cls.step_create_release(),
        ]
