"""GitHub Actions workflow for deploying to PyPI and GitHub Pages.

This module provides the DeployWorkflowConfigFile class for creating a GitHub Actions
workflow that publishes packages to PyPI and deploys documentation to GitHub Pages
after successful releases.

The workflow:
    - **Publishes Package**: Uploads wheel to PyPI for public distribution
    - **Deploys Documentation**: Builds and deploys MkDocs site to GitHub Pages

This is the final step in the automated release pipeline.

See Also:
    pyrig.rig.configs.workflows.release.ReleaseWorkflowConfigFile
        Must complete successfully before this workflow runs
    PyPI: https://pypi.org/
    GitHub Pages: https://pages.github.com/
"""

from typing import Any

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.workflows.release import ReleaseWorkflowConfigFile


class DeployWorkflowConfigFile(WorkflowConfigFile):
    """GitHub Actions workflow for deploying to PyPI and GitHub Pages.

    Generates a .github/workflows/deploy.yml file that publishes the package
    to PyPI and deploys documentation to GitHub Pages after successful releases.

    The workflow:
        - Triggers after ReleaseWorkflowConfigFile completes successfully
        - Builds a Python wheel and publishes it to PyPI when `PYPI_TOKEN` is configured
        - Builds MkDocs documentation site
        - Deploys documentation to GitHub Pages

    Deployment Process:
        1. Build Python wheel
        2. Publish to PyPI using `PYPI_TOKEN` (skips publishing if token is not set)
        3. Build MkDocs documentation site
        4. Deploy to GitHub Pages via GitHub Actions Pages deployment

    Examples:
        Generate deploy.yml workflow::

            from pyrig.rig.configs.workflows.deploy import DeployWorkflowConfigFile

            # Creates .github/workflows/deploy.yml
            DeployWorkflowConfigFile.I.validate()

    Note:
        Publishing to PyPI is token-based by default (via the `PYPI_TOKEN` secret).
        If `PYPI_TOKEN` is not configured, the PyPI publish step is skipped.

    See Also:
        pyrig.rig.configs.workflows.release.ReleaseWorkflowConfigFile
            Triggers this workflow on completion
        pyrig.rig.configs.docs.mkdocs.MkdocsConfigFile
            Configures the documentation site
        PyPI API tokens: https://pypi.org/help/#apitoken
    """

    def workflow_triggers(self) -> dict[str, Any]:
        """Get the workflow triggers.

        Returns:
            Trigger for release workflow completion.
        """
        triggers = super().workflow_triggers()
        triggers.update(
            self.on_workflow_run(
                workflows=[ReleaseWorkflowConfigFile.I.workflow_name()]
            )
        )
        return triggers

    def jobs(self) -> dict[str, Any]:
        """Get the workflow jobs.

        Returns:
            Dict with the publish and deploy jobs.
        """
        jobs: dict[str, Any] = {}
        jobs.update(self.job_publish_package())
        jobs.update(self.job_deploy_documentation())
        return jobs

    def job_publish_package(self) -> dict[str, Any]:
        """Get the publish job configuration.

        Returns:
            Job that builds and publishes to PyPI.
        """
        return self.job(
            job_func=self.job_publish_package,
            steps=self.steps_publish_package(),
            if_condition=self.if_workflow_run_is_success(),
        )

    def job_deploy_documentation(self) -> dict[str, Any]:
        """Get the deploy documentation job configuration.

        Returns:
            Job that deploys documentation to GitHub Pages.
        """
        return self.job(
            job_func=self.job_deploy_documentation,
            permissions={"pages": "write", "id-token": "write"},
            steps=self.steps_deploy_documentation(),
            if_condition=self.if_workflow_run_is_success(),
        )

    def steps_publish_package(self) -> list[dict[str, Any]]:
        """Get the steps for publishing.

        Returns:
            List of steps for setup, build, and publish.
        """
        return [
            *self.steps_core_setup(),
            self.step_build_wheel(),
            self.step_publish_to_pypi(),
        ]

    def steps_deploy_documentation(self) -> list[dict[str, Any]]:
        """Get the steps for deploying documentation.

        Returns:
            List of steps for setup and deploy.
        """
        return [
            *self.steps_core_installed_setup(),
            self.step_build_documentation(),
            self.step_enable_pages(),
            self.step_upload_documentation(),
            self.step_deploy_documentation(),
        ]
