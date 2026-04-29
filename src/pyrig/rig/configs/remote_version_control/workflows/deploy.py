"""GitHub Actions workflow for deploying to PyPI and GitHub Pages.

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
    ``ReleaseWorkflowConfigFile`` completes. Both jobs are gated on a successful
    triggering run.

    Two jobs are defined:

    - **publish-package**: Builds a Python wheel and publishes it to PyPI.
      Publishing is conditional on the ``PYPI_TOKEN`` secret being present;
      the step is skipped when the secret is absent.
    - **deploy-documentation**: Builds the MkDocs documentation site and
      deploys it to GitHub Pages. Requires ``pages: write`` and
      ``id-token: write`` job-level permissions.

    Example:
        Generate or validate the workflow file::

            from pyrig.rig.configs.remote_version_control.workflows.deploy import (
                DeployWorkflowConfigFile,
            )

            DeployWorkflowConfigFile.I.validate()
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
        ``ReleaseWorkflowConfigFile`` completes. Both jobs further guard
        themselves with an ``if`` condition checked via
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

    def jobs(self) -> ConfigDict:
        """Build the top-level jobs configuration.

        Returns:
            Dict containing the publish-package and deploy-documentation jobs.
        """
        jobs: ConfigDict = {}
        jobs.update(self.job_publish_package())
        jobs.update(self.job_deploy_documentation())
        return jobs

    def job_publish_package(self) -> ConfigDict:
        """Build the job that packages and publishes the project to PyPI.

        The job runs only when the triggering workflow run succeeded. Steps
        are provided by :meth:`steps_publish_package`.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        return self.job(
            job_func=self.job_publish_package,
            steps=self.steps_publish_package(),
            if_condition=self.if_workflow_run_is_success(),
        )

    def job_deploy_documentation(self) -> ConfigDict:
        """Build the job that deploys the MkDocs documentation to GitHub Pages.

        Requests ``pages: write`` and ``id-token: write`` permissions at the
        job level, which are required by the GitHub Pages deployment API. The
        job runs only when the triggering workflow run succeeded. Steps are
        provided by :meth:`steps_deploy_documentation`.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        return self.job(
            job_func=self.job_deploy_documentation,
            permissions={"pages": "write", "id-token": "write"},
            steps=self.steps_deploy_documentation(),
            if_condition=self.if_workflow_run_is_success(),
        )

    def steps_publish_package(self) -> list[dict[str, Any]]:
        """Build the ordered steps for the publish-package job.

        Combines core setup with a wheel build and a conditional PyPI publish.
        The publish step reads ``PYPI_TOKEN`` from secrets and echoes a skip
        message when the secret is absent.

        Returns:
            Ordered list of step dicts: core setup, build wheel, publish to PyPI.
        """
        return [
            *self.steps_core_setup(),
            self.step_build_wheel(),
            self.step_publish_to_pypi(),
        ]

    def steps_deploy_documentation(self) -> list[dict[str, Any]]:
        """Build the ordered steps for the deploy-documentation job.

        Combines core installed-setup steps with the full documentation build
        and GitHub Pages deployment sequence.

        Returns:
            Ordered list of step dicts: core installed setup, build docs,
            enable Pages, upload artifact, deploy to GitHub Pages.
        """
        return [
            *self.steps_core_installed_setup(),
            self.step_build_documentation(),
            self.step_enable_pages(),
            self.step_upload_documentation(),
            self.step_deploy_documentation(),
        ]
