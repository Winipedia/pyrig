"""Contains the publish workflow.

This workflow is used to publish the package to PyPI with poetry.
"""

from typing import Any

from pyrig.dev.configs.workflows.base.base import Workflow
from pyrig.dev.configs.workflows.release import ReleaseWorkflow


class PublishWorkflow(Workflow):
    """Publish workflow.

    This workflow is triggered by the release workflow.
    It publishes the package to PyPI with poetry.
    """

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Get the workflow triggers."""
        triggers = super().get_workflow_triggers()
        triggers.update(
            cls.on_workflow_run(workflows=[ReleaseWorkflow.get_workflow_name()])
        )
        return triggers

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs."""
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_publish())
        return jobs

    @classmethod
    def job_publish(cls) -> dict[str, Any]:
        """Get the publish job."""
        return cls.get_job(
            job_func=cls.job_publish,
            steps=cls.steps_publish(),
            if_condition=cls.if_workflow_run_is_success(),
        )

    @classmethod
    def steps_publish(cls) -> list[dict[str, Any]]:
        """Get the publish steps."""
        return [
            *cls.steps_core_setup(),
            cls.step_add_pypi_token_to_poetry(),
            cls.step_publish_to_pypi(),
        ]
