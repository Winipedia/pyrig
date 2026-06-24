"""GitHub Actions workflow generator for the health check CI stage."""

from typing import Any, Literal

from pyrig.core.strings import fstring_var_name
from pyrig.rig.cli.make import local
from pyrig.rig.cli.subcommands import mk
from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.tools.dependencies.auditor import DependencyAuditor
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.testers.project import ProjectTester
from pyrig.rig.tools.version_control.hook_manager import (
    VersionControlHookManager,
)


class HealthCheckWorkflowConfigFile(WorkflowConfigFile):
    """Generates the ``health_check.yml`` GitHub Actions workflow.

    This workflow runs code quality checks and tests on every pull request,
    push to the default branch, daily cron schedule, and manual trigger.

    Three jobs run as part of this workflow:

    1. ``health-checks`` — a single-runner job that applies all pre-commit
       hooks (linting, formatting, type checking, security, markdown), and audits
       dependencies for known CVEs.
    2. ``matrix-health-checks`` — a matrix job that runs the full test suite
       with coverage reporting across all supported OS and Python versions.
    3. ``health-check`` — a fan-in job that waits for both jobs above to
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

    def workflow_triggers(self) -> dict[str, Any]:
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

    def jobs(self) -> dict[str, Any]:
        """Return all jobs for the health check workflow.

        Returns:
            Dict containing the ``health-checks`` job, the
            ``matrix-health-checks`` job, and the ``health-check``
            aggregation job.
        """
        jobs: dict[str, Any] = {}
        jobs.update(self.job_health_checks())
        jobs.update(self.job_matrix_health_checks())
        jobs.update(self.job_health_check())
        return jobs

    def job_health_check(self) -> dict[str, Any]:
        """Return the fan-in aggregation job.

        This job depends on both ``health-checks`` and
        ``matrix-health-checks`` completing successfully. Its job ID
        (``"health-check"``) is registered as the sole required status check
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
            needs=[health_checks_job_id, matrix_health_checks_job_id],
            steps=self.steps_aggregate_jobs(),
        )

    def job_matrix_health_checks(self) -> dict[str, Any]:
        """Return the matrix job that runs the test suite across environments.

        Uses a strategy matrix of all supported OS and Python version
        combinations so the test suite is verified on every platform the
        project targets.

        Returns:
            Job configuration with a matrix strategy, dynamic ``runs-on``
            value, and steps for setup and testing.
        """
        return self.job(
            job_func=self.job_matrix_health_checks,
            strategy=self.strategy_matrix_os_and_python_version(),
            runs_on=self.insert_matrix_os(),
            steps=self.steps_matrix_health_checks(),
        )

    def job_health_checks(self) -> dict[str, Any]:
        """Return the single-runner job that applies all code quality checks.

        Runs on a single Ubuntu runner (no matrix) and covers pre-commit hooks
        and dependency auditing.

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
            Python version and run the test suite.
        """
        return [
            *self.steps_core_matrix_setup(
                python_version=self.insert_matrix_python_version(),
                update_dependencies=True,
            ),
            self.step_run_tests(),
        ]

    def steps_health_checks(self) -> list[dict[str, Any]]:
        """Return the steps for the single-runner quality check job.

        Returns:
            Steps that install dependencies, create version-control-ignored
            local files, run all pre-commit hooks (linting, formatting, type
            checking, security, markdown), and audit dependencies for CVEs.
        """
        return [
            *self.steps_core_installed_setup(update_dependencies=True),
            self.step_create_version_control_ignored_files(),
            self.step_run_pre_commit_hooks(),
            self.step_run_dependency_audit(),
        ]

    def step_run_tests(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that runs the test suite with pytest.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that executes pytest with CI-appropriate flags.
        """
        if step is None:
            step = {}
        run = str(PackageManager.I.run_args(*ProjectTester.I.test_args()))
        return self.step(
            step_func=self.step_run_tests,
            run=run,
            step=step,
        )

    def step_create_version_control_ignored_files(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step to create local gitignored files.

        This is needed so that pyrig sync does not fail on the next step
        and all pre commit hooks pass cleanly.
        """
        return self.step(
            step_func=self.step_create_version_control_ignored_files,
            run=str(
                PackageManager.I.run_args(
                    *Pyrigger.I.group_cmd_args(
                        group=fstring_var_name(f"{mk=}"), cmd=local
                    )
                )
            ),
            step=step,
        )

    def step_run_pre_commit_hooks(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that runs all pre-commit hooks via prek.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs the pre-commit hooks.
        """
        return self.step(
            step_func=self.step_run_pre_commit_hooks,
            run=str(
                PackageManager.I.run_args(
                    *VersionControlHookManager.I.run_all_files_stage_pre_commit_args()
                )
            ),
            step=step,
        )

    def step_run_dependency_audit(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that audits dependencies for known vulnerabilities.

        Runs ``pip-audit`` via uv against the installed environment to detect
        CVEs in direct and transitive dependencies.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``uv run pip-audit``.
        """
        return self.step(
            step_func=self.step_run_dependency_audit,
            run=str(PackageManager.I.run_args(*DependencyAuditor.I.audit_args())),
            step=step,
        )

    def step_aggregate_jobs(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a fan-in step used to aggregate matrix job results.

        The job containing this step declares a ``needs`` dependency on the
        sibling jobs, ensuring all runners have finished before this step runs.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that echoes an aggregation message.
        """
        return self.step(
            step_func=self.step_aggregate_jobs,
            run="echo 'Aggregating jobs into one job.'",
            step=step,
        )
