"""GitHub Actions workflow for deploying documentation to GitHub Pages.

Provides the ``DeployWorkflowConfigFile`` class, which generates the
``.github/workflows/deploy.yml`` workflow file. This workflow is the final
step in the automated CI/CD pipeline and runs after a successful release.
"""

from typing import Any

from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.remote_version_control.workflows.release import (
    ReleaseWorkflowConfigFile,
)


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

    def workflow_triggers(self) -> ConfigDict:
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

    def job(self, *args: Any, **kwargs: Any) -> ConfigDict:
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

    def jobs(self) -> ConfigDict:
        """Build the top-level jobs configuration.

        Returns:
            Dict containing the documentation job.
        """
        return {**self.job_documentation()}

    def job_documentation(self) -> ConfigDict:
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
