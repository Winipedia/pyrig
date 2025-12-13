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
        jobs.update(cls.job_build())
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
    def steps_build(cls) -> list[dict[str, Any]]:
        """Get the steps for building artifacts.

        Returns:
            List of build steps, or placeholder if no builders defined.
        """
        return [
            *cls.steps_core_matrix_setup(no_dev=True),
            cls.step_build_artifacts(),
            cls.step_upload_artifacts(),
        ]
