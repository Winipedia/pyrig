"""GitHub Actions workflow configuration for building project artifacts."""

from typing import Any

from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.remote_version_control.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.version_control.version_controller import VersionController


class BuildWorkflowConfigFile(WorkflowConfigFile):
    """GitHub Actions workflow that builds project artifacts.

    Generates ``.github/workflows/build.yml``. The workflow triggers when the
    health check workflow completes on the default branch (excluding scheduled
    runs), builds artifacts across an OS matrix, then uploads them as GitHub
    Actions artifacts for the release workflow to consume.

    Artifacts produced:
        - **Artifacts**: Built with ``pyrig build`` on Ubuntu, Windows, and macOS.

    The artifact job is guarded so it only runs when the triggering health
    check run succeeded *and* was not a scheduled (cron) run. This prevents
    unnecessary artifact builds and downstream releases on nightly health
    check runs.
    """

    def stem(self) -> str:
        """Return the stem used to derive the workflow filename (``build.yml``).

        Returns:
            ``"build"``
        """
        return "build"

    def workflow_triggers(self) -> ConfigDict:
        """Return the triggers for the build workflow.

        Extends the default ``workflow_dispatch`` trigger inherited from the
        base class with a ``workflow_run`` trigger. The ``workflow_run``
        trigger fires whenever the health check workflow completes on the
        default branch, which is the primary way this workflow is invoked in
        CI.

        Returns:
            Trigger configuration dict containing both ``workflow_dispatch``
            and ``workflow_run`` entries.
        """
        triggers = super().workflow_triggers()
        triggers.update(
            self.on_workflow_run(
                workflows=[HealthCheckWorkflowConfigFile.I.workflow_name()],
                branches=[VersionController.I.default_branch()],
            )
        )
        return triggers

    def jobs(self) -> ConfigDict:
        """Return all jobs for the build workflow.

        Returns:
            Dict with a single job that builds artifacts across an OS matrix.
        """
        return {**self.job_artifacts()}

    def job_artifacts(self) -> ConfigDict:
        """Return the job configuration for building artifacts across an OS matrix.

        The job runs only when both of these conditions hold:
            - The triggering health check workflow run completed successfully.
            - The triggering run was not a scheduled (cron) run.

        Uses an OS matrix strategy (Ubuntu, Windows, macOS) so artifacts are
        produced for all supported platforms in parallel.

        Returns:
            Dict mapping the job ID to its configuration, including the OS
            matrix strategy, conditional guard, and artifact build steps.
        """
        return self.job(
            job_func=self.job_artifacts,
            if_condition=self.combined_if(
                self.if_workflow_run_is_success(),
                self.if_workflow_run_is_not_cron_triggered(),
                operator="&&",
            ),
            strategy=self.strategy_matrix_os(),
            runs_on=self.insert_matrix_os(),
            steps=self.steps_artifacts(),
        )

    def steps_artifacts(self) -> list[dict[str, Any]]:
        """Return the ordered steps for the artifact build job.

        Steps (in order):
            1. Core matrix setup — checkout, uv install, dependency install.
            2. Build artifacts (runs ``pyrig build``).
            3. Upload the ``dist/`` directory as a GitHub Actions artifact.

        Returns:
            Ordered list of step configuration dicts.
        """
        return [
            *self.steps_core_matrix_setup(),
            self.step_build_artifacts(),
            self.step_upload_artifacts(),
        ]
