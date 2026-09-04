"""Deployment workflow configuration."""

from types import MethodType
from typing import Any

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.tools.docs.builder import DocsBuilder
from pyrig.rig.tools.packages.manager import PackageManager


class DeployWorkflowConfigFile(WorkflowConfigFile):
    """Workflow configurations for deployments.

    This includes jobs for building and deploying the documentation site
    to GitHub Pages.
    """

    def job(  # noqa: PLR0913
        self,
        method: MethodType,
        *,
        needs: list[str] | None = None,
        strategy: dict[str, Any] | None = None,
        permissions: dict[str, Any] | None = None,
        if_condition: str | None = None,
        runs_on: str = WorkflowConfigFile.UBUNTU_LATEST,
        environment: str | None = None,
        steps: list[dict[str, Any]] | None = None,
        uses: str | None = None,
        secrets: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a deployment job with an environment derived from its ID.

        Args:
            method: Method representing this job; its name is used to derive
                the job ID and default environment name.
            needs: IDs of jobs that must complete before this job starts.
            strategy: Matrix or other strategy configuration.
            permissions: Job-level permissions override.
            if_condition: GitHub Actions conditional expression controlling
                whether the job runs.
            runs_on: Runner label. Defaults to `ubuntu-latest`.
            environment: Deployment environment name. Defaults to the job ID
                when omitted.
            steps: Ordered list of job steps.
            uses: Reference to a reusable workflow instead of job steps.
            secrets: Named secrets to forward to a called workflow.

        Returns:
            A single job configuration keyed by its derived job ID.
        """
        environment = environment or self.job_id_from_method(method)
        return super().job(
            method,
            needs=needs,
            strategy=strategy,
            permissions=permissions,
            if_condition=if_condition,
            runs_on=runs_on,
            environment=environment,
            steps=steps,
            uses=uses,
            secrets=secrets,
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
        """Return a reusable-workflow trigger.

        Returns:
            Workflow-call trigger configuration.
        """
        return self.on_workflow_call()

    def job_documentation(self) -> dict[str, Any]:
        """Build the job that builds and deploys the documentation site.

        Requests `contents: read` to check out the repository, plus
        `pages: write` and `id-token: write` permissions at the job level,
        required by the GitHub Pages deployment API.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        return self.job(
            self.job_documentation,
            permissions={
                **self.permission_contents(),
                **self.permission_id_token(write=True),
                **self.permission_pages(write=True),
            },
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
        """Build a step that enables GitHub Pages.

        Returns:
            Pages-configuration step using the repository token.
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
