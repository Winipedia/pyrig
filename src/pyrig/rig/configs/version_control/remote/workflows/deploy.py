"""GitHub Actions workflow generator for deploying documentation to GitHub Pages."""

from types import MethodType
from typing import Any

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.version_control.remote.workflows.release import (
    ReleaseWorkflowConfigFile,
)
from pyrig.rig.tools.docs.builder import DocsBuilder
from pyrig.rig.tools.packages.manager import PackageManager


class DeployWorkflowConfigFile(WorkflowConfigFile):
    """GitHub Actions workflow that publishes documentation to GitHub Pages.

    Triggered whenever the release workflow completes, but its job only
    runs if that completion was a success.
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
        """Build a job, defaulting `if_condition` to a success-gate condition.

        When `if_condition` is not given, it defaults to a condition that is
        true only if the workflow run that triggered this workflow succeeded.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        if_condition = if_condition or self.if_workflow_run_is_success()
        return super().job(
            method,
            needs=needs,
            strategy=strategy,
            permissions=permissions,
            runs_on=runs_on,
            if_condition=if_condition,
            steps=steps,
        )

    def concurrency_cancel_in_progress(self) -> bool:
        """Return `False`; a deploy run must not be cancelled mid-publish."""
        return False

    def jobs(self) -> dict[str, Any]:
        """Build the top-level jobs configuration.

        Returns:
            Dict containing the documentation job.
        """
        return {**self.job_documentation()}

    def stem(self) -> str:
        """Return `"deploy"`, the workflow file's stem."""
        return "deploy"

    def workflow_triggers(self) -> dict[str, Any]:
        """Return a `workflow_run` trigger for completion of the release workflow.

        Returns:
            Trigger configuration dict with a `workflow_run` entry.
        """
        return self.on_workflow_run(
            workflows=[ReleaseWorkflowConfigFile.I.workflow_name()],
        )

    def job_documentation(self) -> dict[str, Any]:
        """Build the job that builds and deploys the documentation site.

        Requests `pages: write` and `id-token: write` permissions at the job
        level, required by the GitHub Pages deployment API.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        return self.job(
            self.job_documentation,
            permissions={"id-token": "write", "pages": "write"},
            steps=self.steps_documentation(),
        )

    def steps_documentation(self) -> list[dict[str, Any]]:
        """Build the ordered steps for the documentation job.

        Returns:
            Ordered list of step dicts: environment setup, build the
            documentation, enable Pages, upload the artifact, deploy it.
        """
        return [
            *self.steps_core_installed_setup(),
            self.step_build_documentation(),
            self.step_configure_pages(),
            self.step_upload_documentation(),
            self.step_deploy_documentation(),
        ]

    def step_build_documentation(self) -> dict[str, Any]:
        """Build a step that builds the documentation site into the `site/` directory.

        Returns:
            Step that runs the documentation build command.
        """
        return self.step(
            self.step_build_documentation,
            run=str(PackageManager.I.run_args(*DocsBuilder.I.build_args())),
        )

    def step_configure_pages(self) -> dict[str, Any]:
        """Build a step that enables GitHub Pages for the repository.

        Idempotent: running it on a repository where Pages is already enabled
        has no effect.

        Authenticates with `REPO_TOKEN` rather than the automatic
        `GITHUB_TOKEN`: enabling Pages calls
        `POST /repos/{owner}/{repo}/pages`, and for an installation token
        like `GITHUB_TOKEN` that call also requires `administration: write`
        -- a scope the automatic token can never hold -- so it would fail
        with `Resource not accessible by integration`. A fine-grained PAT
        reaches the endpoint with `pages: write` alone.

        Returns:
            Step that enables GitHub Pages using `REPO_TOKEN`.
        """
        return self.step(
            self.step_configure_pages,
            uses="actions/configure-pages@main",
            with_={"enablement": "true", "token": self.insert_repo_token()},
        )

    def step_deploy_documentation(self) -> dict[str, Any]:
        """Build a step that deploys the uploaded Pages artifact to GitHub Pages.

        Requires the job to have `pages: write` and `id-token: write`
        permissions.

        Returns:
            Step using `actions/deploy-pages@main`.
        """
        return self.step(
            self.step_deploy_documentation,
            uses="actions/deploy-pages@main",
        )

    def step_upload_documentation(self) -> dict[str, Any]:
        """Build a step that uploads the `site/` directory as a Pages artifact.

        Returns:
            Step using `actions/upload-pages-artifact@main`.
        """
        return self.step(
            self.step_upload_documentation,
            uses="actions/upload-pages-artifact@main",
            with_={"path": DocsBuilder.I.site_dir().as_posix()},
        )
