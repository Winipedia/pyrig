"""GitHub Actions workflow configuration for building artifacts and container images."""

from typing import Any

from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.remote_version_control.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.version_controller import VersionController


class BuildWorkflowConfigFile(WorkflowConfigFile):
    """GitHub Actions workflow that builds Python wheels and a container image.

    Generates ``.github/workflows/build.yml``. The workflow triggers when the
    health check workflow completes on the default branch (excluding scheduled
    runs), builds Python wheels across an OS matrix and a container image on
    Ubuntu, then uploads both as GitHub Actions artifacts for the release
    workflow to consume.

    Artifacts produced:
        - **Python wheels**: Built with ``uv build`` on Ubuntu, Windows, and macOS.
        - **Container image**: Built with Podman, saved as a
          ``dist/<project>.tar`` archive.

    Both artifact jobs are guarded so they only run when the triggering health
    check run succeeded *and* was not a scheduled (cron) run. This prevents
    unnecessary artifact builds and downstream releases on nightly health
    check runs.

    Examples:
        Generate the ``build.yml`` workflow file::

            from pyrig.rig.configs.remote_version_control.workflows.build import (
                BuildWorkflowConfigFile,
            )

            BuildWorkflowConfigFile.I.validate()
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
            Dict with two jobs: one that builds Python wheels across an OS
            matrix and one that builds the container image on Ubuntu.
        """
        jobs: ConfigDict = {}
        jobs.update(self.job_build_artifacts())
        jobs.update(self.job_build_container_image())
        return jobs

    def job_build_artifacts(self) -> ConfigDict:
        """Return the job configuration for building Python wheels across an OS matrix.

        The job runs only when both of these conditions hold:
            - The triggering health check workflow run completed successfully.
            - The triggering run was not a scheduled (cron) run.

        Uses an OS matrix strategy (Ubuntu, Windows, macOS) so wheels are
        produced for all supported platforms in parallel.

        Returns:
            Dict mapping the job ID to its configuration, including the OS
            matrix strategy, conditional guard, and artifact build steps.
        """
        return self.job(
            job_func=self.job_build_artifacts,
            if_condition=self.combined_if(
                self.if_workflow_run_is_success(),
                self.if_workflow_run_is_not_cron_triggered(),
                operator="&&",
            ),
            strategy=self.strategy_matrix_os(),
            runs_on=self.insert_matrix_os(),
            steps=self.steps_build_artifacts(),
        )

    def job_build_container_image(self) -> ConfigDict:
        """Return the job configuration for building the project container image.

        The job runs only when both of these conditions hold:
            - The triggering health check workflow run completed successfully.
            - The triggering run was not a scheduled (cron) run.

        Runs on a single Ubuntu runner because container image builds target
        Linux deployments and do not require a cross-platform matrix.

        Returns:
            Dict mapping the job ID to its configuration, including the
            conditional guard and container build steps.
        """
        return self.job(
            job_func=self.job_build_container_image,
            if_condition=self.combined_if(
                self.if_workflow_run_is_success(),
                self.if_workflow_run_is_not_cron_triggered(),
                operator="&&",
            ),
            runs_on=self.UBUNTU_LATEST,
            steps=self.steps_build_container_image(),
        )

    def steps_build_artifacts(self) -> list[dict[str, Any]]:
        """Return the ordered steps for the artifact build job.

        Steps (in order):
            1. Core matrix setup — checkout, git config, uv install, patch
               version bump, dependency upgrade and install, stage lock-file
               changes.
            2. Build artifacts (runs ``pyrig build``).
            3. Upload the ``dist/`` directory as a GitHub Actions artifact.

        Returns:
            Ordered list of step configuration dicts.
        """
        return [
            *self.steps_core_matrix_setup(patch_version=True),
            self.step_build_artifacts(),
            self.step_upload_artifacts(),
        ]

    def steps_build_container_image(self) -> list[dict[str, Any]]:
        """Return the ordered steps for the container image build job.

        Steps (in order):
            1. Core setup — checkout, git config, uv install, patch version
               bump, dependency upgrade and install, stage lock-file changes.
            2. Install Podman as the container engine.
            3. Build the container image from the project's Containerfile.
            4. Save (export) the image to ``dist/<project>.tar``.
            5. Upload the tar archive as a ``container-image`` artifact.

        Returns:
            Ordered list of step configuration dicts.
        """
        return [
            *self.steps_core_setup(patch_version=True),
            self.step_install_container_engine(),
            self.step_build_container_image(),
            self.step_save_container_image(),
            self.step_upload_artifacts(name="container-image"),
        ]
