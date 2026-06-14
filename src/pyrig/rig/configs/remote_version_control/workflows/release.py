"""Workflow configuration for automated GitHub release creation."""

from typing import Any

from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.remote_version_control.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.version_control.version_controller import VersionController


class ReleaseWorkflowConfigFile(WorkflowConfigFile):
    """Generates the ``release.yml`` GitHub Actions workflow.

    This workflow is triggered when the health check workflow completes on the
    default branch. The release job only runs when the triggering run succeeded
    and was not a scheduled (cron) run, so the daily health check run does not
    create a release every day. It creates and pushes a version tag, generates
    a changelog from commit history, and publishes a GitHub release.

    Release process (in order):
        1. Check out the repository (authenticated with the automatic
           ``GITHUB_TOKEN``) and install the uv package manager.
        2. Create a version tag (e.g. ``1.2.3``) and push it to the remote.
        3. Export the version string to ``GITHUB_OUTPUT``.
        4. Generate a changelog from commits since the last tag.
        5. Publish the GitHub release with the changelog body.

    Permissions required:
        - ``contents: write`` — push the version tag and create the release.
    """

    def stem(self) -> str:
        """Return the workflow filename stem.

        Returns:
            ``"release"``, which produces ``release.yml`` as the output file.
        """
        return "release"

    def workflow_triggers(self) -> ConfigDict:
        """Build the workflow trigger configuration.

        Extends the default ``workflow_dispatch`` trigger (inherited from the
        base class) with a ``workflow_run`` trigger that fires when
        :class:`~pyrig.rig.configs.remote_version_control.workflows.health_check.HealthCheckWorkflowConfigFile`
        completes on the default branch.

        Returns:
            Trigger configuration containing both ``workflow_dispatch`` and
            ``workflow_run`` triggers.
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
        """Build the complete jobs configuration for the workflow.

        Returns:
            Dict containing the single release job.
        """
        return {**self.job_distributions()}

    def job_distributions(self) -> ConfigDict:
        """Build the release job configuration.

        The job runs only when both of these conditions hold:
            - The triggering health check workflow run completed successfully.
            - The triggering run was not a scheduled (cron) run.

        The cron guard prevents the daily scheduled health check run from
        creating a release every day.

        Requests ``contents: write`` permission at the job level, which is
        required to push the version tag and create the GitHub release.

        Returns:
            Job configuration dict keyed by the job name, containing the
            guard condition and the ordered release steps.
        """
        return self.job(
            job_func=self.job_distributions,
            if_condition=self.combined_if(
                self.if_workflow_run_is_success(),
                self.if_workflow_run_is_not_cron_triggered(),
                operator="&&",
            ),
            permissions={"contents": "write"},
            steps=self.steps_distributions(),
        )

    def steps_distributions(self) -> list[dict[str, Any]]:
        """Build the ordered list of steps for the release job.

        Returns:
            Steps that perform the full release sequence: environment setup,
            creating and pushing the version tag, exporting the version,
            generating a changelog, and publishing the GitHub release.
        """
        return [
            *self.steps_core_setup(),
            self.step_create_tag(),
            self.step_push_tag(),
            self.step_extract_version(),
            self.step_build_changelog(),
            self.step_create_release(),
        ]
