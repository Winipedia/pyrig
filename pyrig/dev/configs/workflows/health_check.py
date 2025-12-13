"""GitHub Actions workflow for health checks and CI.

This module provides the HealthCheckWorkflow class for creating
a workflow that runs on pull requests, pushes, and scheduled intervals
to verify code quality and run tests.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import pyrig
from pyrig.dev.configs.workflows.base.base import Workflow
from pyrig.dev.utils.packages import get_src_package
from pyrig.src.modules.package import DependencyGraph


class HealthCheckWorkflow(Workflow):
    """Workflow for continuous integration health checks.

    Triggers on pull requests, pushes to main, and scheduled intervals.
    Runs linting, type checking, security scanning, and tests across
    a matrix of OS and Python versions.
    """

    BASE_CRON_HOUR = 0

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Get the workflow triggers.

        Returns:
            Triggers for pull requests, pushes, and scheduled runs.
        """
        triggers = super().get_workflow_triggers()
        triggers.update(cls.on_pull_request())
        triggers.update(cls.on_push())
        triggers.update(cls.on_schedule(cron=cls.get_staggered_cron()))
        return triggers

    @classmethod
    def get_staggered_cron(cls) -> str:
        """Get a staggered cron schedule based on dependency depth.

        Packages with more dependencies run later to avoid conflicts
        when dependencies release right before dependent packages.

        Returns:
            Cron expression with hour offset based on dependency depth.
        """
        offset = cls.get_dependency_offset()
        base_time = datetime.now(tz=UTC).replace(
            hour=cls.BASE_CRON_HOUR, minute=0, second=0, microsecond=0
        )
        scheduled_time = base_time + timedelta(hours=offset)
        return f"0 {scheduled_time.hour} * * *"

    @classmethod
    def get_dependency_offset(cls) -> int:
        """Calculate hour offset based on dependency depth to pyrig.

        Returns:
            Number of hours to offset from base cron hour.
        """
        graph = DependencyGraph()
        src_pkg = get_src_package()
        return graph.shortest_path_length(src_pkg.__name__, pyrig.__name__)

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs.

        Returns:
            Dict with matrix and aggregation jobs.
        """
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_health_check_matrix())
        jobs.update(cls.job_health_check())
        return jobs

    @classmethod
    def job_health_check_matrix(cls) -> dict[str, Any]:
        """Get the matrix job that runs across OS and Python versions.

        Returns:
            Job configuration for matrix testing.
        """
        return cls.get_job(
            job_func=cls.job_health_check_matrix,
            strategy=cls.strategy_matrix_os_and_python_version(),
            runs_on=cls.insert_matrix_os(),
            steps=cls.steps_health_check_matrix(),
        )

    @classmethod
    def job_health_check(cls) -> dict[str, Any]:
        """Get the aggregation job that depends on matrix completion.

        Returns:
            Job configuration for result aggregation.
        """
        return cls.get_job(
            job_func=cls.job_health_check,
            needs=[cls.make_id_from_func(cls.job_health_check_matrix)],
            steps=cls.steps_aggregate_matrix_results(),
        )

    @classmethod
    def steps_health_check_matrix(cls) -> list[dict[str, Any]]:
        """Get the steps for the matrix health check job.

        Returns:
            List of steps for setup, linting, and testing.
        """
        return [
            *cls.steps_core_matrix_setup(
                python_version=cls.insert_matrix_python_version(),
            ),
            cls.step_protect_repository(),
            cls.step_run_pre_commit_hooks(),
            cls.step_run_tests(),
            cls.step_upload_coverage_report(),
        ]

    @classmethod
    def steps_aggregate_matrix_results(cls) -> list[dict[str, Any]]:
        """Get the steps for aggregating matrix results.

        Returns:
            List with the aggregation step.
        """
        return [
            cls.step_aggregate_matrix_results(),
        ]
