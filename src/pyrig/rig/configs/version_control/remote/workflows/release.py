"""Workflow configuration for automated GitHub release creation."""

from typing import Any

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

    def jobs(self) -> dict[str, Any]:
        """Return all jobs for the release workflow.

        Returns:
            Dict containing the health check, publish, and deploy jobs, in
            dependency order.
        """
        return {
            **self.job_health_check(),
            **self.job_publish(),
            **self.job_deploy(),
        }

    def concurrency_cancel_in_progress(self) -> bool:
        """Return `False`; a release run must not be cancelled mid-publish."""
        return False

    def stem(self) -> str:
        """Return `"release"`, the workflow file's stem."""
        return "release"

    def workflow_triggers(self) -> dict[str, Any]:
        """Return a `push` trigger for the default branch.

        Returns:
            Trigger configuration dict with a `push` entry.
        """
        return self.on_push()

    def job_health_check(self) -> dict[str, Any]:
        """Return the health check job configuration.

        Returns:
            Reusable job configuration with its required permissions and secrets.
        """
        secrets = HealthCheckWorkflowConfigFile.I.used_secrets_mapping() or None
        permissions = HealthCheckWorkflowConfigFile.I.used_permissions() or None
        return self.job(
            self.job_health_check,
            uses=HealthCheckWorkflowConfigFile.I.workflow_call_reference(),
            permissions=permissions,
            secrets=secrets,
        )

    def job_publish(self) -> dict[str, Any]:
        """Return the job that creates the version tag and GitHub release.

        Requires the health check job to have passed first. Requests
        `contents: write` permission at the job level, required to create
        the version tag and the GitHub release.

        Returns:
            Job configuration dict keyed by the job ID, containing the
            ordered release steps.
        """
        return self.job(
            self.job_publish,
            needs=[self.job_id_from_method(self.job_health_check)],
            permissions=self.permission_contents(write=True),
            steps=self.steps_publish(),
        )

    def job_deploy(self) -> dict[str, Any]:
        """Return the deployment job configuration.

        Returns:
            Reusable job configuration that runs after publishing.
        """
        secrets = DeployWorkflowConfigFile.I.used_secrets_mapping() or None
        permissions = DeployWorkflowConfigFile.I.used_permissions() or None
        return self.job(
            self.job_deploy,
            uses=DeployWorkflowConfigFile.I.workflow_call_reference(),
            needs=[self.job_id_from_method(self.job_publish)],
            permissions=permissions,
            secrets=secrets,
        )

    def steps_publish(self) -> list[dict[str, Any]]:
        """Return the ordered steps for the release job.

        Returns:
            Steps that create and publish the GitHub release.
        """
        return [
            *self.steps_core_setup(),
            self.step_create_release(),
        ]

    def step_create_release(self) -> dict[str, Any]:
        """Build a step that creates a version tag and GitHub release.

        Returns:
            Release-creation step with generated release notes.
        """
        version = self.shell_insert_version()
        return self.step(
            self.step_create_release,
            run=RemoteVersionController.I.create_release_args(tag=version).multiline(),
            env={"GH_TOKEN": self.insert_github_token()},
        )
