"""GitHub Actions workflow for health checks and CI.

This module provides the HealthCheckWorkflow class for creating a GitHub Actions
workflow that runs continuous integration checks to verify code quality and
functionality.

The workflow runs:
    - **On Pull Requests**: Validates changes before merging
    - **On Pushes to Main**: Ensures main branch stays healthy
    - **On Schedule**: Daily checks with staggered timing based on dependency depth

    Checks Performed:
        - **Linting**: ruff check for code quality
        - **Formatting**: ruff format for code style
        - **Type Checking**: ty check for type safety
        - **Security (code)**: bandit for vulnerability scanning
        - **Security (dependencies)**: pip-audit for dependency vulnerability scanning
        - **Markdown**: rumdl for documentation quality
        - **Tests**: pytest with coverage reporting

The workflow uses a matrix strategy to test across:
    - Multiple OS (Ubuntu, macOS, Windows)
    - Multiple Python versions (from pyproject.toml)

See Also:
    GitHub Actions: https://docs.github.com/en/actions
    pyrig.dev.configs.base.workflow.Workflow
        Base class for workflow generation
"""

from datetime import UTC, datetime, timedelta
from importlib import import_module
from typing import Any

import pyrig
from pyrig.dev.configs.base.workflow import Workflow
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.package import DependencyGraph


class HealthCheckWorkflow(Workflow):
    """GitHub Actions workflow for continuous integration health checks.

    Generates a .github/workflows/health_check.yaml file that runs comprehensive
    code quality checks and tests on pull requests, pushes, and scheduled intervals.

    The workflow includes:
        - **Quality Checks**: Linting, formatting, type checking, security scanning
        - **Tests**: pytest with coverage reporting across OS and Python version matrix
        - **Staggered Scheduling**: Daily runs with timing based on dependency depth
          to avoid conflicts when dependencies release updates

    Triggers:
        - Pull requests to any branch
        - Pushes to main branch
        - Scheduled daily runs (staggered by dependency depth)

    Matrix Strategy:
        - OS: Ubuntu (latest), macOS (latest), Windows (latest)
        - Python: All supported versions from pyproject.toml

    Examples:
        Generate health_check.yaml workflow::

            from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow

            # Creates .github/workflows/health_check.yaml
            HealthCheckWorkflow()

    See Also:
        pyrig.dev.configs.workflows.build.BuildWorkflow
            Runs after this workflow completes on main branch (excludes cron)
        pyrig.dev.configs.base.workflow.Workflow
            Base class with workflow generation utilities
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
        graph = DependencyGraph.cached()
        src_pkg = import_module(PyprojectConfigFile.L.get_package_name())
        return graph.shortest_path_length(src_pkg.__name__, pyrig.__name__)

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs.

        Returns:
            Dict with protect, matrix, and aggregation jobs.
        """
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_health_checks())
        jobs.update(cls.job_matrix_health_checks())
        jobs.update(cls.job_health_check())
        return jobs

    @classmethod
    def job_health_check(cls) -> dict[str, Any]:
        """Get the aggregation job that depends on matrix completion.

        Returns:
            Job configuration for result aggregation.
        """
        matrix_health_checks_job_id = cls.make_id_from_func(
            cls.job_matrix_health_checks
        )
        health_checks_job_id = cls.make_id_from_func(cls.job_health_checks)
        return cls.get_job(
            job_func=cls.job_health_check,
            needs=[matrix_health_checks_job_id, health_checks_job_id],
            steps=cls.steps_aggregate_jobs(),
        )

    @classmethod
    def job_matrix_health_checks(cls) -> dict[str, Any]:
        """Get the matrix job that runs across OS and Python versions.

        Returns:
            Job configuration for matrix testing.
        """
        return cls.get_job(
            job_func=cls.job_matrix_health_checks,
            strategy=cls.strategy_matrix_os_and_python_version(),
            runs_on=cls.insert_matrix_os(),
            steps=cls.steps_matrix_health_checks(),
        )

    @classmethod
    def job_health_checks(cls) -> dict[str, Any]:
        """Get the job that runs health checks.

        This is for non matrix checks.

        Returns:
            Job configuration for health checks.
        """
        return cls.get_job(
            job_func=cls.job_health_checks,
            steps=cls.steps_health_checks(),
        )

    @classmethod
    def steps_matrix_health_checks(cls) -> list[dict[str, Any]]:
        """Get the steps for the matrix health check job.

        Returns:
            List of steps for setup and testing.
        """
        return [
            *cls.steps_core_matrix_setup(
                python_version=cls.insert_matrix_python_version(),
            ),
            cls.step_run_tests(),
            cls.step_upload_coverage_report(),
        ]

    @classmethod
    def steps_aggregate_jobs(cls) -> list[dict[str, Any]]:
        """Get the steps for aggregating matrix results.

        Returns:
            List with the aggregation step.
        """
        return [
            cls.step_aggregate_jobs(),
        ]

    @classmethod
    def steps_health_checks(cls) -> list[dict[str, Any]]:
        """Get the steps for the health check job.

        Returns:
            List of steps for setup, linting, and testing.
        """
        return [
            *cls.steps_core_installed_setup(),
            cls.step_run_pre_commit_hooks(),
            cls.step_run_dependency_audit(),
            cls.step_protect_repository(),
        ]
