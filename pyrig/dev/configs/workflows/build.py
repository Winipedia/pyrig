"""GitHub Actions workflow for building artifacts.

This module provides the BuildWorkflow class for creating
a workflow that builds artifacts across OS matrix after
successful health checks on main branch.
"""

from typing import Any

from pyrig.dev.configs.workflows.base.base import Workflow
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow


class BuildWorkflow(Workflow):
    """Workflow for building project artifacts.

    Triggers after health check workflow completes on main branch.
    Builds artifacts across OS matrix and uploads them for the
    release workflow to use.
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
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs.

        Returns:
            Dict with build job.
        """
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_build_artifacts())
        jobs.update(cls.job_build_container_image())
        return jobs

    @classmethod
    def job_build_artifacts(cls) -> dict[str, Any]:
        """Get the build job that runs across OS matrix.

        Returns:
            Job configuration for building artifacts.
        """
        return cls.get_job(
            job_func=cls.job_build_artifacts,
            if_condition=cls.if_workflow_run_is_success(),
            strategy=cls.strategy_matrix_os(),
            runs_on=cls.insert_matrix_os(),
            steps=cls.steps_build_artifacts(),
        )

    @classmethod
    def job_build_container_image(cls) -> dict[str, Any]:
        """Get the build job that builds the container image.

        Returns:
            Job configuration for building container image.
        """
        return cls.get_job(
            job_func=cls.job_build_container_image,
            if_condition=cls.if_workflow_run_is_success(),
            runs_on=cls.UBUNTU_LATEST,
            steps=cls.steps_build_container_image(),
        )

    @classmethod
    def steps_build_artifacts(cls) -> list[dict[str, Any]]:
        """Get the steps for building artifacts.

        Returns:
            List of build steps, or placeholder if no builders defined.
        """
        return [
            *cls.steps_core_matrix_setup(),
            cls.step_build_artifacts(),
            cls.step_upload_artifacts(),
        ]

    @classmethod
    def steps_build_container_image(cls) -> list[dict[str, Any]]:
        """Get the steps for building the container image.

        Returns:
            List of build steps.
        """
        return [
            cls.step_checkout_repository(),
            cls.step_install_container_engine(),
            cls.step_build_container_image(),
            cls.step_make_dist_folder(),
            cls.step_save_container_image(),
            cls.step_upload_artifacts(name="container-image"),
        ]
