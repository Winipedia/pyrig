"""Deployment workflow configuration."""

from collections.abc import Callable
from typing import Any, override

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.version_control.remote.workflows.documentation import (
    DocumentationWorkflowConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.repository import (
    RepositoryWorkflowConfigFile,
)


class DeployWorkflowConfigFile(WorkflowConfigFile):
    """Orchestrate the reusable deployment workflows."""

    @override
    def concurrency_cancel_in_progress(self) -> bool:
        """Return `False`; a deploy run must not be cancelled mid-publish."""
        return False

    @override
    def jobs(self) -> tuple[Callable[[], dict[str, Any]], ...]:
        """Return the repository and documentation workflow calls."""
        return (self.job_repository, self.job_documentation)

    @override
    def stem(self) -> str:
        """Return the workflow file stem, `deploy`."""
        return "deploy"

    @override
    def workflow_triggers(self) -> dict[str, Any]:
        """Return a reusable-workflow trigger."""
        return self.on_workflow_call()

    def job_documentation(self) -> dict[str, Any]:
        """Return the reusable documentation deployment job."""
        return self.job_workflow_call(
            self.job_documentation,
            workflow=DocumentationWorkflowConfigFile,
        )

    def job_repository(self) -> dict[str, Any]:
        """Return the reusable repository-configuration job."""
        return self.job_workflow_call(
            self.job_repository,
            workflow=RepositoryWorkflowConfigFile,
        )
