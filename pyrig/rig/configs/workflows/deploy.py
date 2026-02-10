"""GitHub Actions workflow for deploying to PyPI and GitHub Pages.

This module provides the DeployWorkflow class for creating a GitHub Actions
workflow that publishes packages to PyPI and deploys documentation to GitHub Pages
after successful releases.

The workflow:
    - **Publishes Package**: Uploads wheel to PyPI for public distribution
    - **Deploys Documentation**: Builds and deploys MkDocs site to GitHub Pages

This is the final step in the automated release pipeline.

See Also:
    pyrig.rig.configs.workflows.release.ReleaseWorkflow
        Must complete successfully before this workflow runs
    PyPI: https://pypi.org/
    GitHub Pages: https://pages.github.com/
"""

from typing import Any

from pyrig.rig.configs.base.workflow import Workflow
from pyrig.rig.configs.workflows.release import ReleaseWorkflow


class DeployWorkflow(Workflow):
    """GitHub Actions workflow for deploying to PyPI and GitHub Pages.

    Generates a .github/workflows/deploy.yml file that publishes the package
    to PyPI and deploys documentation to GitHub Pages after successful releases.

    The workflow:
        - Triggers after ReleaseWorkflow completes successfully
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

            from pyrig.rig.configs.workflows.deploy import DeployWorkflow

            # Creates .github/workflows/deploy.yml
            DeployWorkflow()

    Note:
        Publishing to PyPI is token-based by default (via the `PYPI_TOKEN` secret).
        If `PYPI_TOKEN` is not configured, the PyPI publish step is skipped.

    See Also:
        pyrig.rig.configs.workflows.release.ReleaseWorkflow
            Triggers this workflow on completion
        pyrig.rig.configs.docs.mkdocs.MkdocsConfigFile
            Configures the documentation site
        PyPI API tokens: https://pypi.org/help/#apitoken
    """

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Get the workflow triggers.

        Returns:
            Trigger for release workflow completion.
        """
        triggers = super().get_workflow_triggers()
        triggers.update(
            cls.on_workflow_run(workflows=[ReleaseWorkflow.get_workflow_name()])
        )
        return triggers

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs.

        Returns:
            Dict with the publish and deploy jobs.
        """
        jobs: dict[str, Any] = {}
        jobs.update(cls.job_publish_package())
        jobs.update(cls.job_deploy_documentation())
        return jobs

    @classmethod
    def job_publish_package(cls) -> dict[str, Any]:
        """Get the publish job configuration.

        Returns:
            Job that builds and publishes to PyPI.
        """
        return cls.get_job(
            job_func=cls.job_publish_package,
            steps=cls.steps_publish_package(),
            if_condition=cls.if_workflow_run_is_success(),
        )

    @classmethod
    def job_deploy_documentation(cls) -> dict[str, Any]:
        """Get the deploy documentation job configuration.

        Returns:
            Job that deploys documentation to GitHub Pages.
        """
        return cls.get_job(
            job_func=cls.job_deploy_documentation,
            permissions={"pages": "write", "id-token": "write"},
            steps=cls.steps_deploy_documentation(),
            if_condition=cls.if_workflow_run_is_success(),
        )

    @classmethod
    def steps_publish_package(cls) -> list[dict[str, Any]]:
        """Get the steps for publishing.

        Returns:
            List of steps for setup, build, and publish.
        """
        return [
            *cls.steps_core_setup(),
            cls.step_build_wheel(),
            cls.step_publish_to_pypi(),
        ]

    @classmethod
    def steps_deploy_documentation(cls) -> list[dict[str, Any]]:
        """Get the steps for deploying documentation.

        Returns:
            List of steps for setup and deploy.
        """
        return [
            *cls.steps_core_installed_setup(),
            cls.step_build_documentation(),
            cls.step_enable_pages(),
            cls.step_upload_documentation(),
            cls.step_deploy_documentation(),
        ]
