"""GitHub Actions workflow for deploying documentation to GitHub Pages.

Provides the ``DeployWorkflowConfigFile`` class, which generates the
``.github/workflows/deploy.yml`` workflow file. This workflow is the final
step in the automated CI/CD pipeline and runs after a successful release.
"""

from typing import Any

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.version_control.remote.workflows.release import (
    ReleaseWorkflowConfigFile,
)
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.package_manager import PackageManager


class DeployWorkflowConfigFile(WorkflowConfigFile):
    """Generates the GitHub Actions workflow for deployment.

    Produces ``.github/workflows/deploy.yml``, which runs automatically when
    ``ReleaseWorkflowConfigFile`` completes. The job is gated on a successful
    triggering run.

    One job is defined:

    - **documentation**: Builds the MkDocs documentation site and
      deploys it to GitHub Pages. Requires ``pages: write`` and
      ``id-token: write`` job-level permissions.
    """

    def stem(self) -> str:
        """Return the stem used to name the generated workflow file.

        Returns:
            ``"deploy"``, which produces ``.github/workflows/deploy.yml``.
        """
        return "deploy"

    def workflow_triggers(self) -> dict[str, Any]:
        """Build the workflow trigger configuration.

        Extends the default ``workflow_dispatch`` trigger inherited from the
        base class with a ``workflow_run`` trigger that fires whenever
        ``ReleaseWorkflowConfigFile`` completes. The job further guards
        itself with an ``if`` condition checked via
        :meth:`if_workflow_run_is_success`.

        Returns:
            Combined trigger dict with ``workflow_dispatch`` and
            ``workflow_run`` entries.
        """
        triggers = super().workflow_triggers()
        triggers.update(
            self.on_workflow_run(
                workflows=[ReleaseWorkflowConfigFile.I.workflow_name()]
            )
        )
        return triggers

    def job(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Build a job gated on the triggering workflow run succeeding.

        Overrides :meth:`WorkflowConfigFile.job` to inject an ``if`` condition
        (via :meth:`if_workflow_run_is_success`) into every job in this
        workflow, so jobs run only when the triggering ``workflow_run`` event
        reports a successful conclusion.

        Args:
            *args: Positional arguments forwarded to
                :meth:`WorkflowConfigFile.job`.
            **kwargs: Keyword arguments forwarded to
                :meth:`WorkflowConfigFile.job`.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        return super().job(
            *args, if_condition=self.if_workflow_run_is_success(), **kwargs
        )

    def jobs(self) -> dict[str, Any]:
        """Build the top-level jobs configuration.

        Returns:
            Dict containing the documentation job.
        """
        return {**self.job_documentation()}

    def job_documentation(self) -> dict[str, Any]:
        """Build the job that deploys the MkDocs documentation to GitHub Pages.

        Requests ``pages: write`` and ``id-token: write`` permissions at the
        job level, which are required by the GitHub Pages deployment API. The
        job runs only when the triggering workflow run succeeded. Steps are
        provided by :meth:`steps_documentation`.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        return self.job(
            job_func=self.job_documentation,
            permissions={"pages": "write", "id-token": "write"},
            steps=self.steps_documentation(),
        )

    def steps_documentation(self) -> list[dict[str, Any]]:
        """Build the ordered steps for the documentation job.

        Combines core installed-setup steps with the full documentation build
        and GitHub Pages deployment sequence.

        Returns:
            Ordered list of step dicts: core installed setup, build docs,
            enable Pages, upload artifact, deploy to GitHub Pages.
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
        """Build a step that generates the MkDocs documentation site.

        Runs the docs builder command, which invokes ``mkdocs build`` and
        writes the rendered HTML site to the ``site/`` directory.  The
        ``site/`` directory is then consumed by the subsequent
        :meth:`step_upload_documentation` step.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs the docs builder command.
        """
        return self.step(
            step_func=self.step_build_documentation,
            run=str(PackageManager.I.run_args(*DocsBuilder.I.build_args())),
            step=step,
        )

    def step_configure_pages(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that enables GitHub Pages for the repository.

        Calls ``actions/configure-pages`` with ``enablement: true``.  This is
        idempotent -- running it on a repository where Pages is already enabled
        has no effect.

        Authenticates with ``REPO_TOKEN`` rather than the automatic
        ``GITHUB_TOKEN``: enabling Pages calls ``POST /repos/{owner}/{repo}/pages``.
        A fine-grained PAT reaches that endpoint with ``pages: write`` alone, but
        for an installation token like ``GITHUB_TOKEN`` the same call also requires
        ``administration: write`` -- a scope the automatic token can never hold --
        so it would fail with ``Resource not accessible by integration``.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that enables GitHub Pages using ``REPO_TOKEN``.
        """
        return self.step(
            step_func=self.step_configure_pages,
            uses="actions/configure-pages@main",
            with_={"token": self.insert_repo_token(), "enablement": "true"},
            step=step,
        )

    def step_upload_documentation(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that uploads the documentation as a Pages artifact.

        Uploads the ``site/`` directory produced by
        :meth:`step_build_documentation` so that the Pages deployment step
        can publish it.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using ``actions/upload-pages-artifact@main``.
        """
        return self.step(
            step_func=self.step_upload_documentation,
            uses="actions/upload-pages-artifact@main",
            with_={"path": "site"},
            step=step,
        )

    def step_deploy_documentation(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that deploys the uploaded Pages artifact to GitHub Pages.

        Must be preceded by :meth:`step_upload_documentation`.  The job that
        contains this step must have ``pages: write`` and
        ``id-token: write`` permissions.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using ``actions/deploy-pages@main``.
        """
        return self.step(
            step_func=self.step_deploy_documentation,
            uses="actions/deploy-pages@main",
            step=step,
        )
