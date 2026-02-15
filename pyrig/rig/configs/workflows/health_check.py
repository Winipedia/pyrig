"""GitHub Actions workflow for health checks and CI.

This module provides the HealthCheckWorkflowConfigFile class
for creating a GitHub Actions workflow that runs continuous
integration checks to verify code quality and
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
    pyrig.rig.configs.base.workflow.WorkflowConfigFile
        Base class for workflow generation
"""

from datetime import UTC, datetime, timedelta
from importlib import import_module
from typing import Any

import pyrig
from pyrig.rig.configs.base.base import ConfigDict
from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.src.dependency_graph import DependencyGraph


class HealthCheckWorkflowConfigFile(WorkflowConfigFile):
    """GitHub Actions workflow for continuous integration health checks.

    Generates a .github/workflows/health_check.yml file that runs comprehensive
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
        Generate health_check.yml workflow::

            from pyrig.rig.configs.workflows.health_check import (
                HealthCheckWorkflowConfigFile
            )

            # Creates .github/workflows/health_check.yml
            HealthCheckWorkflowConfigFile.I.validate()

    See Also:
        pyrig.rig.configs.workflows.build.BuildWorkflowConfigFile
            Runs after this workflow completes on main branch (excludes cron)
        pyrig.rig.configs.base.workflow.WorkflowConfigFile
            Base class with workflow generation utilities
    """

    BASE_CRON_HOUR = 0

    def workflow_triggers(self) -> ConfigDict:
        """Get the workflow triggers.

        Returns:
            Triggers for pull requests, pushes, and scheduled runs.
        """
        triggers = super().workflow_triggers()
        triggers.update(self.on_pull_request())
        triggers.update(self.on_push())
        triggers.update(self.on_schedule(cron=self.staggered_cron()))
        return triggers

    def staggered_cron(self) -> str:
        """Get a staggered cron schedule based on dependency depth.

        Packages with more dependencies run later to avoid conflicts
        when dependencies release right before dependent packages.

        Returns:
            Cron expression with hour offset based on dependency depth.
        """
        offset = self.dependency_offset()
        base_time = datetime.now(tz=UTC).replace(
            hour=self.BASE_CRON_HOUR, minute=0, second=0, microsecond=0
        )
        scheduled_time = base_time + timedelta(hours=offset)
        return f"0 {scheduled_time.hour} * * *"

    def dependency_offset(self) -> int:
        """Calculate hour offset based on dependency depth to pyrig.

        Returns:
            Number of hours to offset from base cron hour.
        """
        graph = DependencyGraph()
        src_package = import_module(PyprojectConfigFile.I.package_name())
        return graph.shortest_path_length(src_package.__name__, pyrig.__name__)

    def jobs(self) -> ConfigDict:
        """Get the workflow jobs.

        Returns:
            Dict with health check, matrix health check, and aggregation jobs.
        """
        jobs: ConfigDict = {}
        jobs.update(self.job_health_checks())
        jobs.update(self.job_matrix_health_checks())
        jobs.update(self.job_health_check())
        return jobs

    def job_health_check(self) -> ConfigDict:
        """Get the aggregation job that depends on matrix completion.

        Returns:
            Job configuration for result aggregation.
        """
        matrix_health_checks_job_id = self.make_id_from_func(
            self.job_matrix_health_checks
        )
        health_checks_job_id = self.make_id_from_func(self.job_health_checks)
        return self.job(
            job_func=self.job_health_check,
            needs=[matrix_health_checks_job_id, health_checks_job_id],
            steps=self.steps_aggregate_jobs(),
        )

    def job_matrix_health_checks(self) -> ConfigDict:
        """Get the matrix job that runs across OS and Python versions.

        Returns:
            Job configuration for matrix testing.
        """
        return self.job(
            job_func=self.job_matrix_health_checks,
            strategy=self.strategy_matrix_os_and_python_version(),
            runs_on=self.insert_matrix_os(),
            steps=self.steps_matrix_health_checks(),
        )

    def job_health_checks(self) -> ConfigDict:
        """Get the job that runs health checks.

        This is for non-matrix checks.

        Returns:
            Job configuration for health checks.
        """
        return self.job(
            job_func=self.job_health_checks,
            steps=self.steps_health_checks(),
        )

    def steps_matrix_health_checks(self) -> list[dict[str, Any]]:
        """Get the steps for the matrix health check job.

        Returns:
            List of steps for setup and testing.
        """
        return [
            *self.steps_core_matrix_setup(
                python_version=self.insert_matrix_python_version(),
            ),
            self.step_run_tests(),
            self.step_upload_coverage_report(),
        ]

    def steps_aggregate_jobs(self) -> list[dict[str, Any]]:
        """Get the steps for aggregating matrix results.

        Returns:
            List with the aggregation step.
        """
        return [
            self.step_aggregate_jobs(),
        ]

    def steps_health_checks(self) -> list[dict[str, Any]]:
        """Get the steps for the health check job.

        Returns:
            List of steps for setup, pre-commit hooks, dependency audit,
            and repository protection.
        """
        return [
            *self.steps_core_installed_setup(),
            self.step_run_pre_commit_hooks(),
            self.step_run_dependency_audit(),
            self.step_protect_repository(),
        ]
