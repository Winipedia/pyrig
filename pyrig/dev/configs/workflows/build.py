"""GitHub Actions workflow for building artifacts.

This module provides the BuildWorkflow class for creating a GitHub Actions
workflow that builds project artifacts and container images after successful
health checks on the main branch.

The workflow builds:
    - **Python Wheels**: Distribution packages for PyPI
    - **Container Images**: Docker/Podman images for deployment

Artifacts are uploaded and made available for the release workflow to create
GitHub releases.

The publish workflow runs after a successful release and handles publishing to
PyPI and GitHub Pages.

See Also:
    pyrig.dev.configs.workflows.health_check.HealthCheckWorkflow
        Must complete successfully before this workflow runs
    pyrig.dev.configs.workflows.release.ReleaseWorkflow
        Uses artifacts from this workflow
"""

from typing import Any

from pyrig.dev.configs.base.workflow import Workflow
from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow
from pyrig.dev.management.version_controller import VersionController


class BuildWorkflow(Workflow):
    """GitHub Actions workflow for building project artifacts.

    Generates a .github/workflows/build.yaml file that builds Python wheels and
    container images after health checks pass on the main branch.

    The workflow:
        - Triggers after HealthCheckWorkflow completes on main branch
        - Skips cron-triggered health checks (only push/dispatch triggers build)
        - Builds Python wheels across OS matrix
        - Builds container images (Containerfile/Dockerfile)
        - Uploads artifacts for the release workflow

    Artifacts Built:
        - **Python Wheels**: Built with uv, uploaded as GitHub artifacts
        - **Container Images**: Built with Docker/Podman, tagged with version

    Examples:
        Generate build.yaml workflow::

            from pyrig.dev.configs.workflows.build import BuildWorkflow

            # Creates .github/workflows/build.yaml
            BuildWorkflow()

    See Also:
        pyrig.dev.configs.workflows.health_check.HealthCheckWorkflow
            Triggers this workflow on completion
        pyrig.dev.configs.workflows.release.ReleaseWorkflow
            Downloads and uses artifacts from this workflow
        pyrig.dev.configs.containers.container_file.ContainerfileConfigFile
            Generates the Containerfile used for image builds
    """

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Get the workflow triggers.

        Returns:
            Trigger for health check completion on main.
        """
        triggers = super().get_workflow_triggers()
        triggers.update(
            cls.on_workflow_run(
                workflows=[HealthCheckWorkflow.get_workflow_name()],
                branches=[VersionController.L.get_default_branch()],
            )
        )
        return triggers

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs.

        Returns:
            Dict with build job.
        """
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_build_artifacts())
        jobs.update(cls.job_build_container_image())
        return jobs

    @classmethod
    def job_build_artifacts(cls) -> dict[str, Any]:
        """Get the build job that runs across OS matrix.

        Returns:
            Job configuration for building artifacts.
        """
        return cls.get_job(
            job_func=cls.job_build_artifacts,
            if_condition=cls.combined_if(
                cls.if_workflow_run_is_success(),
                cls.if_workflow_run_is_not_cron_triggered(),
                operator="&&",
            ),
            strategy=cls.strategy_matrix_os(),
            runs_on=cls.insert_matrix_os(),
            steps=cls.steps_build_artifacts(),
        )

    @classmethod
    def job_build_container_image(cls) -> dict[str, Any]:
        """Get the build job that builds the container image.

        Returns:
            Job configuration for building container image.
        """
        return cls.get_job(
            job_func=cls.job_build_container_image,
            if_condition=cls.combined_if(
                cls.if_workflow_run_is_success(),
                cls.if_workflow_run_is_not_cron_triggered(),
                operator="&&",
            ),
            runs_on=cls.UBUNTU_LATEST,
            steps=cls.steps_build_container_image(),
        )

    @classmethod
    def steps_build_artifacts(cls) -> list[dict[str, Any]]:
        """Get the steps for building artifacts.

        Returns:
            List of build steps, or placeholder if no builders defined.
        """
        return [
            *cls.steps_core_matrix_setup(),
            cls.step_build_artifacts(),
            cls.step_upload_artifacts(),
        ]

    @classmethod
    def steps_build_container_image(cls) -> list[dict[str, Any]]:
        """Get the steps for building the container image.

        Returns:
            List of build steps.
        """
        return [
            cls.step_checkout_repository(),
            cls.step_install_container_engine(),
            cls.step_build_container_image(),
            cls.step_make_dist_folder(),
            cls.step_save_container_image(),
            cls.step_upload_artifacts(name="container-image"),
        ]
