"""Workflow configuration for automated GitHub release creation."""

from types import MethodType
from typing import Any

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.version_control.remote.configure import (
    ConfigureRepositoryConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.version_control.controller import VersionController
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class ReleaseWorkflowConfigFile(WorkflowConfigFile):
    """Generator for the `release.yml` GitHub Actions workflow.

    The workflow is triggered by completion of the health check workflow on
    the default branch, but its job only proceeds when that health check run
    both succeeded and was itself triggered by a push — so the daily
    scheduled run and pull request runs never produce a release.
    A qualifying run applies repository settings and protection rulesets,
    enables private vulnerability reporting, and publishes a GitHub release
    with auto-generated release notes, tagging the current version in the
    same call.
    """

    def job(  # noqa: PLR0913
        self,
        method: MethodType,
        *,
        needs: list[str] | None = None,
        strategy: dict[str, Any] | None = None,
        permissions: dict[str, Any] | None = None,
        runs_on: str = WorkflowConfigFile.UBUNTU_LATEST,
        if_condition: str | None = None,
        steps: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Build a job gated by default on a successful, push-triggered run.

        Args:
            method: Method to build the job.
            needs: IDs of jobs that must complete before this job starts.
            strategy: Matrix or other strategy configuration.
            permissions: Job-level permissions override.
            runs_on: Runner label. Defaults to `ubuntu-latest`.
            if_condition: GitHub Actions conditional expression controlling
                whether the job runs. Defaults to requiring the triggering
                run to have succeeded and been push-triggered.
            steps: Ordered list of step configurations.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        if_condition = (
            if_condition or self.if_workflow_run_is_success_and_push_triggered()
        )
        return super().job(
            method,
            needs=needs,
            strategy=strategy,
            permissions=permissions,
            runs_on=runs_on,
            if_condition=if_condition,
            steps=steps,
        )

    def jobs(self) -> dict[str, Any]:
        """Return all jobs for the release workflow.

        Returns:
            Dict containing the single release job.
        """
        return {**self.job_publish()}

    def concurrency_cancel_in_progress(self) -> bool:
        """Return `False`; a release run must not be cancelled mid-publish."""
        return False

    def stem(self) -> str:
        """Return `"release"`, the workflow file's stem."""
        return "release"

    def workflow_triggers(self) -> dict[str, Any]:
        """Return the triggers for the release workflow.

        A single `workflow_run` trigger that fires when the health check
        workflow completes on the default branch.

        Returns:
            Trigger configuration dict with a `workflow_run` entry.
        """
        return self.on_workflow_run(
            workflows=[HealthCheckWorkflowConfigFile.I.workflow_name()],
            branches=[VersionController.I.default_branch()],
        )

    def job_publish(self) -> dict[str, Any]:
        """Return the job that configures and releases the project.

        Requests `contents: write` permission at the job level, which is
        required to create the version tag and the GitHub release.

        Returns:
            Job configuration dict keyed by the job ID, containing the
            guard condition and the ordered release steps.
        """
        return self.job(
            self.job_publish,
            permissions={"contents": "write"},
            steps=self.steps_publish(),
        )

    def steps_publish(self) -> list[dict[str, Any]]:
        """Return the ordered steps for the release job.

        Returns:
            Steps that perform the full release sequence: environment setup,
            applying repository settings and rulesets, enabling private
            vulnerability reporting, and publishing the GitHub release.
        """
        return [
            *self.steps_core_setup(),
            self.step_configure_repository(),
            self.step_create_release(),
        ]

    def step_create_release(self) -> dict[str, Any]:
        """Build a step that creates a version tag and GitHub release.

        Uses the `gh` CLI (preinstalled on GitHub-hosted runners) to create
        a release named and tagged with the current project version, using
        GitHub's auto-generated release notes as its body. If no tag
        named after the current version exists yet, `gh` creates one.

        Returns:
            Step that runs `gh release create`.
        """
        version = self.shell_insert_version()
        return self.step(
            self.step_create_release,
            run=RemoteVersionController.I.create_release_args(tag=version).multiline(),
            env={"GH_TOKEN": self.insert_github_token()},
        )

    def step_configure_repository(self) -> dict[str, Any]:
        """Build a step that applies repository settings via the GitHub API.

        Runs the generated configuration script, which invokes every
        function it defines in turn: applying general repository settings,
        creating or updating all rulesets, and enabling private
        vulnerability reporting. A function added to
        `ConfigureRepositoryConfigFile` runs automatically as part of this
        step, without a corresponding change here.

        Returns:
            Step that runs the configuration script.
        """
        return self.step(
            self.step_configure_repository,
            run=f"bash {ConfigureRepositoryConfigFile.I.path().as_posix()}",
            env={"GH_TOKEN": self.insert_repo_token()},
        )
