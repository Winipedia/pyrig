"""Deployment workflow configuration."""

from collections.abc import Callable
from types import MethodType
from typing import Any, override

from pyrig.core.subprocesses import Args
from pyrig.rig import resources
from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.version_control.remote.configure import (
    ConfigureRepositoryConfigFile,
)
from pyrig.rig.tools.docs.builder import DocsBuilder
from pyrig.rig.tools.formatting.shell import ShellFormatter
from pyrig.rig.tools.packages.manager import PackageManager


class DeployWorkflowConfigFile(WorkflowConfigFile):
    """Workflow configuration for deployment-style jobs."""

    @override
    def concurrency_cancel_in_progress(self) -> bool:
        """Return `False`; a deploy run must not be cancelled mid-publish."""
        return False

    @override
    def jobs(self) -> tuple[Callable[[], dict[str, Any]], ...]:
        """Return the deployment job builders.

        Returns:
            Tuple containing repository, documentation build, and deployment builders.
        """
        return (
            self.job_repository,
            self.job_build_documentation,
            self.job_deploy_documentation,
        )

    @override
    def stem(self) -> str:
        """Return the workflow file stem, `deploy`."""
        return "deploy"

    @override
    def workflow_triggers(self) -> dict[str, Any]:
        """Return a reusable-workflow trigger.

        Returns:
            Workflow-call trigger configuration.
        """
        return self.on_workflow_call()

    def job_deploy_documentation(self) -> dict[str, Any]:
        """Build the job that deploys the uploaded documentation site.

        Returns:
            Job configuration for deploying the Pages artifact after the build.
        """
        return self.job(
            self.job_deploy_documentation,
            needs=self.job_deploy_documentation_needs(),
            environment="documentation",
            permissions=self.job_deploy_documentation_permissions(),
            steps=self.steps_deploy_documentation(),
            timeout_minutes=30,
        )

    def job_repository(self) -> dict[str, Any]:
        """Build the job that applies repository-level configuration.

        Returns:
            Job configuration for applying repository-level settings.
        """
        return self.job(
            self.job_repository,
            environment="repository",
            permissions=self.job_repository_permissions(),
            steps=self.steps_repository(),
            timeout_minutes=10,
        )

    def job_deploy_documentation_needs(self) -> tuple[MethodType, ...]:
        """Return the documentation build prerequisite for deployment.

        Returns:
            Tuple containing the documentation build job.
        """
        return (self.job_build_documentation,)

    def job_deploy_documentation_permissions(self) -> dict[str, str]:
        """Return the permissions for the documentation deployment job.

        Requests only `pages: write` and `id-token: write`, required by the
        GitHub Pages deployment API. No repository checkout is needed.

        Returns:
            Permissions mapping for the documentation job.
        """
        return {
            **self.permission_id_token(write=True),
            **self.permission_pages(write=True),
        }

    def job_repository_permissions(self) -> dict[str, str]:
        """Return the permissions for the repository job.

        Requests `contents: read` to check out the repository; the
        configuration step itself authenticates separately via `REPO_TOKEN`,
        not `GITHUB_TOKEN`.

        Returns:
            Permissions mapping for the repository job.
        """
        return self.permission_contents()

    def steps_deploy_documentation(self) -> list[dict[str, Any]]:
        """Build the ordered steps for the documentation deployment job.

        Returns:
            Pages enablement followed by deployment of the uploaded artifact.
        """
        return [
            self.step_configure_pages(),
            self.step_deploy_documentation(),
        ]

    def steps_repository(self) -> list[dict[str, Any]]:
        """Build the ordered steps for the repository job.

        Returns:
            Checkout followed by the repository-configuration step.
        """
        return [
            self.step_checkout_repository(),
            self.step_configure_repository(),
        ]

    def job_build_documentation(self) -> dict[str, Any]:
        """Build the job that builds and uploads the documentation site.

        Returns:
            Job configuration for building and uploading the Pages artifact.
        """
        return self.job(
            self.job_build_documentation,
            permissions=self.job_build_documentation_permissions(),
            steps=self.steps_build_documentation(),
            timeout_minutes=60,
        )

    def step_configure_pages(self) -> dict[str, Any]:
        """Build a step that enables GitHub Pages.

        Uses `actions/configure-pages`, defaulting to
        `action_configure_pages()`.

        Returns:
            Pages-configuration step using the repository token.
        """
        return self.step(
            self.step_configure_pages,
            uses=self.action_configure_pages(),
            with_={
                "enablement": "true",
                "token": self.insert_repo_token(),
            },
        )

    def step_configure_repository(self) -> dict[str, Any]:
        """Build a step that applies repository configuration.

        Returns:
            Repository-configuration step.
        """
        return self.step(
            self.step_configure_repository,
            run=str(
                Args(
                    ShellFormatter.I.dialect(),
                    ConfigureRepositoryConfigFile.I.path().as_posix(),
                ),
            ),
            env={"GH_TOKEN": self.insert_repo_token()},
        )

    def step_deploy_documentation(self) -> dict[str, Any]:
        """Build a step that deploys the uploaded Pages artifact to GitHub Pages.

        Uses `actions/deploy-pages`, defaulting to `action_deploy_pages()`.

        Requires the job to have `pages: write` and `id-token: write`
        permissions.

        Returns:
            Step using `actions/deploy-pages@<ref>`.
        """
        return self.step(
            self.step_deploy_documentation,
            uses=self.action_deploy_pages(),
        )

    def action_configure_pages(self) -> tuple[str, str, str]:
        """Return action metadata for `actions/configure-pages`.

        Returns:
            Tuple of action name, pinned commit SHA, and release tag.
        """
        return self.action_from_resource(self.action_configure_pages, resources)

    def action_deploy_pages(self) -> tuple[str, str, str]:
        """Return action metadata for `actions/deploy-pages`.

        Returns:
            Tuple of action name, pinned commit SHA, and release tag.
        """
        return self.action_from_resource(self.action_deploy_pages, resources)

    def job_build_documentation_permissions(self) -> dict[str, str]:
        """Return read-only checkout permissions for the documentation build.

        Returns:
            Permissions mapping granting `contents: read`.
        """
        return self.permission_contents()

    def steps_build_documentation(self) -> list[dict[str, Any]]:
        """Build the ordered steps for the documentation build job.

        Returns:
            Environment setup, documentation build, and Pages artifact upload.
        """
        return [
            *self.steps_core_installed_setup(),
            self.step_build_documentation(),
            self.step_upload_documentation(),
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

    def step_upload_documentation(self) -> dict[str, Any]:
        """Build a step that uploads the `site/` directory as a Pages artifact.

        Uses `actions/upload-pages-artifact`, defaulting to
        `action_upload_pages_artifact()`.

        Returns:
            Step using `actions/upload-pages-artifact@<ref>`.
        """
        return self.step(
            self.step_upload_documentation,
            uses=self.action_upload_pages_artifact(),
            with_={"path": DocsBuilder.I.site_dir().as_posix()},
        )

    def action_upload_pages_artifact(self) -> tuple[str, str, str]:
        """Return action metadata for `actions/upload-pages-artifact`.

        Returns:
            Tuple of action name, pinned commit SHA, and release tag.
        """
        return self.action_from_resource(self.action_upload_pages_artifact, resources)
