"""GitHub Actions workflow for building artifacts.

This module provides the BuildWorkflowConfigFile class for creating a GitHub Actions
workflow that builds project artifacts and container images after successful
health checks on the main branch.

The workflow builds:
    - **Python Wheels**: Distribution packages for PyPI
    - **Container Images**: Docker/Podman images for deployment

Artifacts are uploaded and made available for the release workflow to create
GitHub releases.

See Also:
    pyrig.rig.configs.workflows.health_check.HealthCheckWorkflowConfigFile
        Must complete successfully before this workflow runs
    pyrig.rig.configs.workflows.release.ReleaseWorkflowConfigFile
        Uses artifacts from this workflow
"""

from typing import Any

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.workflows.health_check import HealthCheckWorkflowConfigFile
from pyrig.rig.tools.version_controller import VersionController


class BuildWorkflowConfigFile(WorkflowConfigFile):
    """GitHub Actions workflow for building project artifacts.

    Generates a .github/workflows/build.yml file that builds Python wheels and
    container images after health checks pass on the main branch.

    The workflow:
        - Triggers after HealthCheckWorkflowConfigFile completes on main branch
        - Skips cron-triggered health checks (only push/dispatch triggers build)
        - Builds Python wheels across OS matrix
        - Builds container images (Containerfile/Dockerfile)
        - Uploads artifacts for the release workflow

    Artifacts Built:
        - **Python Wheels**: Built with uv, uploaded as GitHub artifacts
        - **Container Images**: Built with Docker/Podman, tagged with version

    Examples:
        Generate build.yml workflow::

            from pyrig.rig.configs.workflows.build import BuildWorkflowConfigFile

            # Creates .github/workflows/build.yml
            BuildWorkflowConfigFile.I.validate()

    See Also:
        pyrig.rig.configs.workflows.health_check.HealthCheckWorkflowConfigFile
            Triggers this workflow on completion
        pyrig.rig.configs.workflows.release.ReleaseWorkflowConfigFile
            Downloads and uses artifacts from this workflow
        pyrig.rig.configs.containers.container_file.ContainerfileConfigFile
            Generates the Containerfile used for image builds
    """

    def workflow_triggers(self) -> dict[str, Any]:
        """Get the workflow triggers.

        Returns:
            Trigger for health check completion on main.
        """
        triggers = super().workflow_triggers()
        triggers.update(
            self.on_workflow_run(
                workflows=[HealthCheckWorkflowConfigFile.I.workflow_name()],
                branches=[VersionController.I.default_branch()],
            )
        )
        return triggers

    def jobs(self) -> dict[str, Any]:
        """Get the workflow jobs.

        Returns:
            Dict with build job.
        """
        jobs: dict[str, Any] = {}
        jobs.update(self.job_build_artifacts())
        jobs.update(self.job_build_container_image())
        return jobs

    def job_build_artifacts(self) -> dict[str, Any]:
        """Get the build job that runs across OS matrix.

        Returns:
            Job configuration for building artifacts.
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

    def job_build_container_image(self) -> dict[str, Any]:
        """Get the build job that builds the container image.

        Returns:
            Job configuration for building container image.
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
        """Get the steps for building artifacts.

        Returns:
            List of build steps.
        """
        return [
            *self.steps_core_matrix_setup(patch_version=True),
            self.step_build_artifacts(),
            self.step_upload_artifacts(),
        ]

    def steps_build_container_image(self) -> list[dict[str, Any]]:
        """Get the steps for building the container image.

        Returns:
            List of build steps.
        """
        return [
            *self.steps_core_setup(patch_version=True),
            self.step_install_container_engine(),
            self.step_build_container_image(),
            self.step_save_container_image(),
            self.step_upload_artifacts(name="container-image"),
        ]
