"""Reusable workflow for building and deploying documentation."""

from collections.abc import Callable
from types import MethodType
from typing import Any, override

from pyrig.rig import resources
from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.tools.docs.builder import DocsBuilder
from pyrig.rig.tools.packages.manager import PackageManager


class DocumentationWorkflowConfigFile(WorkflowConfigFile):
    """Build and deploy the documentation site to GitHub Pages."""

    @override
    def concurrency_cancel_in_progress(self) -> bool:
        """Return `False`; documentation deployment must not be cancelled."""
        return False

    @override
    def jobs(self) -> tuple[Callable[[], dict[str, Any]], ...]:
        """Return the documentation build and deploy jobs."""
        return (self.job_build, self.job_deploy)

    @override
    def workflow_triggers(self) -> dict[str, Any]:
        """Return a reusable-workflow trigger."""
        return self.on_workflow_call()

    @override
    def stem(self) -> str:
        """Return the workflow file stem, `documentation`."""
        return "documentation"

    def job_deploy(self) -> dict[str, Any]:
        """Deploy the Pages artifact after the build succeeds."""
        return self.job(
            self.job_deploy,
            needs=self.job_deploy_needs(),
            environment=self.stem(),
            permissions=self.job_deploy_permissions(),
            steps=self.steps_deploy(),
            timeout_minutes=30,
        )

    def job_deploy_needs(self) -> tuple[MethodType, ...]:
        """Return the documentation build prerequisite."""
        return (self.job_build,)

    def job_deploy_permissions(self) -> dict[str, str]:
        """Return the permissions required to deploy GitHub Pages."""
        return {
            **self.permission_id_token(write=True),
            **self.permission_pages(write=True),
        }

    def steps_deploy(self) -> list[dict[str, Any]]:
        """Return Pages enablement and deployment steps."""
        return [self.step_configure_pages(), self.step_deploy_documentation()]

    def job_build(self) -> dict[str, Any]:
        """Build the documentation site and upload its Pages artifact."""
        return self.job(
            self.job_build,
            permissions=self.job_build_permissions(),
            steps=self.steps_build(),
            timeout_minutes=60,
        )

    def step_configure_pages(self) -> dict[str, Any]:
        """Enable GitHub Pages using the repository token."""
        return self.step(
            self.step_configure_pages,
            uses=self.action_configure_pages(),
            with_={"enablement": "true", "token": self.insert_repo_token()},
        )

    def step_deploy_documentation(self) -> dict[str, Any]:
        """Deploy the uploaded Pages artifact."""
        return self.step(
            self.step_deploy_documentation,
            uses=self.action_deploy_pages(),
        )

    def action_configure_pages(self) -> tuple[str, str, str]:
        """Return action metadata for `actions/configure-pages`."""
        return self.action_from_resource(self.action_configure_pages, resources)

    def action_deploy_pages(self) -> tuple[str, str, str]:
        """Return action metadata for `actions/deploy-pages`."""
        return self.action_from_resource(self.action_deploy_pages, resources)

    def job_build_permissions(self) -> dict[str, str]:
        """Return read-only repository permissions for checkout."""
        return self.permission_contents()

    def steps_build(self) -> list[dict[str, Any]]:
        """Return setup, documentation build, and Pages artifact upload."""
        return [
            *self.steps_core_installed_setup(),
            self.step_build_documentation(),
            self.step_upload_documentation(),
        ]

    def step_build_documentation(self) -> dict[str, Any]:
        """Build the documentation site into the configured site directory."""
        return self.step(
            self.step_build_documentation,
            run=str(PackageManager.I.run_args(*DocsBuilder.I.build_args())),
        )

    def step_upload_documentation(self) -> dict[str, Any]:
        """Upload the documentation site as a Pages artifact."""
        return self.step(
            self.step_upload_documentation,
            uses=self.action_upload_pages_artifact(),
            with_={"path": DocsBuilder.I.site_dir().as_posix()},
        )

    def action_upload_pages_artifact(self) -> tuple[str, str, str]:
        """Return action metadata for `actions/upload-pages-artifact`."""
        return self.action_from_resource(self.action_upload_pages_artifact, resources)
