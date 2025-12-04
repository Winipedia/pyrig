"""GitHub Actions workflow for publishing to PyPI.

This module provides the PublishWorkflow class for creating
a workflow that publishes the package to PyPI after a successful release.
"""

from typing import Any

from pyrig.dev.configs.workflows.base.base import Workflow
from pyrig.dev.configs.workflows.release import ReleaseWorkflow


class PublishWorkflow(Workflow):
    """Workflow for publishing packages to PyPI.

    Triggers after the release workflow completes successfully.
    Builds a wheel and publishes it to PyPI.
    """

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Get the workflow triggers.

        Returns:
            Trigger for release workflow completion.
        """
        triggers = super().get_workflow_triggers()
        triggers.update(
            cls.on_workflow_run(workflows=[ReleaseWorkflow.get_workflow_name()])
        )
        return triggers

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs.

        Returns:
            Dict with the publish job.
        """
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_publish())
        return jobs

    @classmethod
    def job_publish(cls) -> dict[str, Any]:
        """Get the publish job configuration.

        Returns:
            Job that builds and publishes to PyPI.
        """
        return cls.get_job(
            job_func=cls.job_publish,
            steps=cls.steps_publish(),
            if_condition=cls.if_workflow_run_is_success(),
        )

    @classmethod
    def steps_publish(cls) -> list[dict[str, Any]]:
        """Get the steps for publishing.

        Returns:
            List of steps for setup, build, and publish.
        """
        return [
            *cls.steps_core_setup(),
            cls.step_build_wheel(),
            cls.step_publish_to_pypi(),
        ]
