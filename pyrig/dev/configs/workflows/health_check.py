"""Contains the pull request workflow.

This workflow is used to run tests on pull requests.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import pyrig
from pyrig.dev.configs.workflows.base.base import Workflow
from pyrig.src.modules.package import DependencyGraph


class HealthCheckWorkflow(Workflow):
    """Pull request workflow.

    This workflow is triggered by a pull request.
    It runs tests on the pull request.
    """

    BASE_CRON_HOUR = 1

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Get the workflow triggers."""
        triggers = super().get_workflow_triggers()
        triggers.update(cls.on_pull_request())
        triggers.update(cls.on_push())
        triggers.update(cls.on_schedule(cron=cls.get_staggered_cron()))
        return triggers

    @classmethod
    def get_staggered_cron(cls) -> str:
        """Get the staggered cron schedule based on dependency count.

        Packages with more dependencies run later to avoid conflicts when
        dependencies release right before dependent packages run their tests.
        Base time is 1 AM, with 1 hour added for each dependency on pyrig.
        """
        offset = cls.get_dependency_offset()
        base_time = datetime.now(tz=UTC).replace(
            hour=cls.BASE_CRON_HOUR, minute=0, second=0, microsecond=0
        )
        scheduled_time = base_time + timedelta(hours=offset)
        return f"0 {scheduled_time.hour} * * *"

    @classmethod
    def get_dependency_offset(cls) -> int:
        """Get the hour offset based on the number of dependencies on pyrig.

        Returns:
            The number of hours to offset from the base cron hour.
        """
        graph = DependencyGraph()
        all_depending_on_pyrig = graph.get_all_depending_on(pyrig, include_self=False)
        return len(all_depending_on_pyrig)

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs."""
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_health_check_matrix())
        jobs.update(cls.job_health_check())
        return jobs

    @classmethod
    def job_health_check_matrix(cls) -> dict[str, Any]:
        """Get the health check matrix job."""
        return cls.get_job(
            job_func=cls.job_health_check_matrix,
            strategy=cls.strategy_matrix_os_and_python_version(),
            runs_on=cls.insert_matrix_os(),
            steps=cls.steps_health_check_matrix(),
        )

    @classmethod
    def job_health_check(cls) -> dict[str, Any]:
        """Get the health check job."""
        return cls.get_job(
            job_func=cls.job_health_check,
            needs=[cls.make_id_from_func(cls.job_health_check_matrix)],
            steps=cls.steps_aggregate_matrix_results(),
        )

    @classmethod
    def steps_health_check_matrix(cls) -> list[dict[str, Any]]:
        """Get the health check matrix steps."""
        return [
            *cls.steps_core_matrix_setup(
                python_version=cls.insert_matrix_python_version()
            ),
            cls.step_protect_repository(),
            cls.step_run_pre_commit_hooks(),
            cls.step_run_tests(),
        ]

    @classmethod
    def steps_aggregate_matrix_results(cls) -> list[dict[str, Any]]:
        """Get the aggregate matrix results step."""
        return [
            cls.step_aggregate_matrix_results(),
        ]
