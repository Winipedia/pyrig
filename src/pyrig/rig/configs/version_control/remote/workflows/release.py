"""Workflow configuration for automated GitHub release creation."""

from collections.abc import Callable
from types import MethodType
from typing import Any, override

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.version_control.remote.workflows.deploy import (
    DeployWorkflowConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class ReleaseWorkflowConfigFile(WorkflowConfigFile):
    """GitHub Actions workflow configuration for releasing project changes."""

    @override
    def concurrency_cancel_in_progress(self) -> bool:
        """Return `False`; a release run must not be cancelled mid-publish."""
        return False

    @override
    def jobs(self) -> tuple[Callable[[], dict[str, Any]], ...]:
        """Return all jobs for the release workflow.

        Returns:
            Tuple of health check, publish, and deploy job builders, in dependency
            order.
        """
        return (
            self.job_health_check,
            self.job_publish,
            self.job_deploy,
        )

    @override
    def stem(self) -> str:
        """Return the workflow file stem, `release`."""
        return "release"

    @override
    def workflow_triggers(self) -> dict[str, Any]:
        """Return a `push` trigger for the default branch.

        Returns:
            Trigger configuration dict with a `push` entry.
        """
        return self.on_push()

    def job_deploy(self) -> dict[str, Any]:
        """Return the deployment job configuration.

        Returns:
            Reusable job configuration that runs after publishing.
        """
        return self.job_workflow_call(
            self.job_deploy,
            workflow=DeployWorkflowConfigFile,
            needs=self.job_deploy_needs(),
        )

    def job_deploy_needs(self) -> tuple[MethodType, ...]:
        """Return the prerequisite job for the deployment workflow call.

        Returns:
            Tuple containing the publish job.
        """
        return (self.job_publish,)

    def job_publish(self) -> dict[str, Any]:
        """Return the job that creates the version tag and GitHub release.

        Requires the health check job to have passed first.

        Returns:
            Job configuration with publishing prerequisites, permissions, and
            ordered release steps.
        """
        return self.job(
            self.job_publish,
            needs=self.job_publish_needs(),
            permissions=self.job_publish_permissions(),
            steps=self.steps_publish(),
            timeout_minutes=30,
        )

    def job_publish_needs(self) -> tuple[MethodType, ...]:
        """Return the prerequisite job for publishing a release.

        Returns:
            Tuple containing the health-check workflow job.
        """
        return (self.job_health_check,)

    def job_publish_permissions(self) -> dict[str, str]:
        """Return the permissions for the publish job.

        Requests `contents: write`, required to create the version tag and
        the GitHub release.

        Returns:
            Permissions mapping granting `contents: write`.
        """
        return self.permission_contents(write=True)

    def steps_publish(self) -> list[dict[str, Any]]:
        """Return the ordered steps for the release job.

        Returns:
            Steps that create and publish the GitHub release.
        """
        return [
            *self.steps_core_setup(),
            self.step_extract_version(),
            self.step_create_release(),
        ]

    def job_health_check(self) -> dict[str, Any]:
        """Return the health check job configuration.

        Returns:
            Reusable job configuration with its required permissions and secrets.
        """
        return self.job_workflow_call(
            self.job_health_check,
            workflow=HealthCheckWorkflowConfigFile,
        )

    def step_create_release(self) -> dict[str, Any]:
        """Build a step that creates a version tag and GitHub release.

        Returns:
            Release-creation step with generated release notes.
        """
        return self.step(
            self.step_create_release,
            run=RemoteVersionController.I.create_release_args(
                tag=self.insert_version_expansion(),
            ).multiline(),
            env={
                "GH_TOKEN": self.insert_github_token(),
                self.version_var(): self.insert_output_version(),
            },
        )
