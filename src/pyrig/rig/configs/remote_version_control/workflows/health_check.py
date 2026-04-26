"""GitHub Actions workflow generator for the health check CI stage."""

from typing import Any, Literal

from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.workflow import WorkflowConfigFile


class HealthCheckWorkflowConfigFile(WorkflowConfigFile):
    """Generates the ``health_check.yml`` GitHub Actions workflow.

    This workflow runs code quality checks and tests on every pull request,
    push to the default branch, daily cron schedule, and manual trigger.

    Three jobs run as part of this workflow:

    1. ``health_checks`` — a single-runner job that applies all pre-commit
       hooks (linting, formatting, type checking, security, markdown), audits
       dependencies for known CVEs, and enforces branch protection settings.
    2. ``matrix_health_checks`` — a matrix job that runs the full test suite
       with coverage reporting across all supported OS and Python versions.
    3. ``health_check`` — a fan-in job that waits for both jobs above to
       succeed. Its job ID is registered as the required status check in the
       branch protection ruleset, making it the single gate for merging.
    """

    def stem(self) -> str:
        """Return the stem used to derive the workflow filename.

        Returns:
            ``"health_check"``, giving the path
            ``.github/workflows/health_check.yml``.
        """
        return "health_check"

    def workflow_triggers(self) -> ConfigDict:
        """Return the triggers for the health check workflow.

        Extends the default ``workflow_dispatch`` trigger from the base class
        with pull request, push, and scheduled cron triggers.

        Returns:
            Trigger configuration dict with ``workflow_dispatch``,
            ``pull_request``, ``push``, and ``schedule`` entries.
        """
        triggers = super().workflow_triggers()
        triggers.update(self.on_pull_request())
        triggers.update(self.on_push())
        triggers.update(self.on_schedule(cron=" ".join(map(str, self.cron_schedule()))))
        return triggers

    def cron_schedule(
        self,
    ) -> tuple[
        int | Literal["*"],
        int | Literal["*"],
        int | Literal["*"],
        int | Literal["*"],
        int | Literal["*"],
    ]:
        """Return the cron schedule tuple for the daily workflow run.

        The five-element tuple maps to ``(minute, hour, day, month, weekday)``
        and is joined into a cron string by :meth:`workflow_triggers`.

        Returns:
            ``(0, 1, "*", "*", "*")``, which schedules the workflow every day
            at 01:00 UTC.
        """
        return 0, 1, "*", "*", "*"

    def jobs(self) -> ConfigDict:
        """Return all jobs for the health check workflow.

        Returns:
            Dict containing the ``health_checks`` job, the
            ``matrix_health_checks`` job, and the ``health_check``
            aggregation job.
        """
        jobs: ConfigDict = {}
        jobs.update(self.job_health_checks())
        jobs.update(self.job_matrix_health_checks())
        jobs.update(self.job_health_check())
        return jobs

    def job_health_check(self) -> ConfigDict:
        """Return the fan-in aggregation job.

        This job depends on both ``health_checks`` and
        ``matrix_health_checks`` completing successfully. Its job ID
        (``"health_check"``) is registered as the sole required status check
        in the branch protection ruleset, making it the single gate that must
        pass before any pull request can be merged.

        Returns:
            Job configuration with ``needs`` set to both sibling jobs and a
            single aggregation step.
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
        """Return the matrix job that runs the test suite across environments.

        Uses a strategy matrix of all supported OS and Python version
        combinations so the test suite is verified on every platform the
        project targets.

        Returns:
            Job configuration with a matrix strategy, dynamic ``runs-on``
            value, and steps for setup, testing, and coverage upload.
        """
        return self.job(
            job_func=self.job_matrix_health_checks,
            strategy=self.strategy_matrix_os_and_python_version(),
            runs_on=self.insert_matrix_os(),
            steps=self.steps_matrix_health_checks(),
        )

    def job_health_checks(self) -> ConfigDict:
        """Return the single-runner job that applies all code quality checks.

        Runs on a single Ubuntu runner (no matrix) and covers pre-commit hooks,
        dependency auditing, and branch protection enforcement.

        Returns:
            Job configuration with steps for the full quality check sequence.
        """
        return self.job(
            job_func=self.job_health_checks,
            steps=self.steps_health_checks(),
        )

    def steps_aggregate_jobs(self) -> list[dict[str, Any]]:
        """Return the steps for the fan-in aggregation job.

        Returns:
            A single-element list containing the aggregation echo step.
        """
        return [
            self.step_aggregate_jobs(),
        ]

    def steps_matrix_health_checks(self) -> list[dict[str, Any]]:
        """Return the steps for the matrix test job.

        Returns:
            Steps that set up the environment for the current matrix OS and
            Python version, run the test suite, and upload the coverage report
            to Codecov.
        """
        return [
            *self.steps_core_matrix_setup(
                python_version=self.insert_matrix_python_version(),
            ),
            self.step_run_tests(),
            self.step_upload_coverage_report(),
        ]

    def steps_health_checks(self) -> list[dict[str, Any]]:
        """Return the steps for the single-runner quality check job.

        Returns:
            Steps that install dependencies, run all pre-commit hooks
            (linting, formatting, type checking, security, markdown),
            audit dependencies for CVEs, and apply branch protection rules.
        """
        return [
            *self.steps_core_installed_setup(),
            self.step_run_pre_commit_hooks(),
            self.step_run_dependency_audit(),
            self.step_protect_repository(),
        ]
