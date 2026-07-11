"""GitHub Actions workflow generator for deploying documentation to GitHub Pages."""

from typing import Any

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.version_control.remote.workflows.release import (
    ReleaseWorkflowConfigFile,
)
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.package_manager import PackageManager


class DeployWorkflowConfigFile(WorkflowConfigFile):
    """GitHub Actions workflow that publishes documentation to GitHub Pages.

    Runs automatically when the release workflow completes successfully.
    """

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

    def job(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Build a job gated on the triggering workflow run having succeeded.

        Args:
            *args: Positional arguments forwarded to the base implementation.
            **kwargs: Keyword arguments forwarded to the base implementation.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        return super().job(
            *args,
            if_condition=self.if_workflow_run_is_success(),
            **kwargs,
        )

    def jobs(self) -> dict[str, Any]:
        """Build the top-level jobs configuration.

        Returns:
            Dict containing the documentation job.
        """
        return {**self.job_documentation()}

    def job_documentation(self) -> dict[str, Any]:
        """Build the job that builds and deploys the documentation site.

        Requests `pages: write` and `id-token: write` permissions at the job
        level, required by the GitHub Pages deployment API.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        return self.job(
            self.job_documentation,
            permissions={"pages": "write", "id-token": "write"},
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

    def step_build_documentation(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that builds the documentation site into the `site/` directory.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs the documentation build command.
        """
        return self.step(
            self.step_build_documentation,
            run=str(PackageManager.I.run_args(*DocsBuilder.I.build_args())),
            step=step,
        )

    def step_configure_pages(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
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

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that enables GitHub Pages using `REPO_TOKEN`.
        """
        return self.step(
            self.step_configure_pages,
            uses="actions/configure-pages@main",
            with_={"token": self.insert_repo_token(), "enablement": "true"},
            step=step,
        )

    def step_upload_documentation(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that uploads the `site/` directory as a Pages artifact.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using `actions/upload-pages-artifact@main`.
        """
        return self.step(
            self.step_upload_documentation,
            uses="actions/upload-pages-artifact@main",
            with_={"path": DocsBuilder.I.site_dir().as_posix()},
            step=step,
        )

    def step_deploy_documentation(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that deploys the uploaded Pages artifact to GitHub Pages.

        Requires the job to have `pages: write` and `id-token: write`
        permissions.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using `actions/deploy-pages@main`.
        """
        return self.step(
            self.step_deploy_documentation,
            uses="actions/deploy-pages@main",
            step=step,
        )
