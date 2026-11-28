"""Reusable workflow for applying repository-level configuration."""

from collections.abc import Callable
from typing import Any, override

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.version_control.remote.configure import (
    ConfigureRepositoryConfigFile,
)
from pyrig.rig.tools.linting.shell import ShellLinter


class RepositoryWorkflowConfigFile(WorkflowConfigFile):
    """Apply repository configuration using the repository environment."""

    @override
    def jobs(self) -> tuple[Callable[[], dict[str, Any]], ...]:
        """Return the repository-configuration job."""
        return (self.job_configure,)

    @override
    def workflow_triggers(self) -> dict[str, Any]:
        """Return a reusable-workflow trigger."""
        return self.on_workflow_call()

    @override
    def stem(self) -> str:
        """Return the workflow file stem, `repository`."""
        return "repository"

    def job_configure(self) -> dict[str, Any]:
        """Configure repository settings."""
        return self.job(
            environment=self.stem(),
            permissions=self.permissions_job_configure(),
            steps=self.steps_configure(),
            timeout_minutes=10,
        )

    def permissions_job_configure(self) -> dict[str, str]:
        """Return read-only repository permissions for checkout."""
        return self.permission_contents()

    def steps_configure(self) -> tuple[Callable[[], dict[str, Any]], ...]:
        """Return checkout and repository-configuration steps."""
        return (
            self.step_checkout_repository,
            self.step_configure_repository,
        )

    def step_configure_repository(self) -> dict[str, Any]:
        """Apply repository settings using the repository token."""
        return self.step(
            run=str(
                ShellLinter.I.run_script_args(
                    file=ConfigureRepositoryConfigFile.I.path(),
                ),
            ),
            env={"GH_TOKEN": self.insert_repo_token()},
        )
