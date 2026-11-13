"""Tests for the repository-configuration workflow."""

from pyrig.rig.configs.version_control.remote.configure import (
    ConfigureRepositoryConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.repository import (
    RepositoryWorkflowConfigFile,
)


class TestRepositoryWorkflowConfigFile:
    """Tests for `RepositoryWorkflowConfigFile`."""

    def test_job_configure(self) -> None:
        """Check the repository job environment and permissions."""
        expected_timeout_minutes = 10
        workflow = RepositoryWorkflowConfigFile.I
        job = workflow.job_configure()
        assert job["job_id"] == "configure"
        assert job["environment"] == "repository"
        assert job["permissions"] == {"contents": "read"}
        assert job["timeout-minutes"] == expected_timeout_minutes
        assert job["steps"] == workflow.steps_configure()

    def test_jobs(self) -> None:
        """Check the workflow includes its configuration job."""
        workflow = RepositoryWorkflowConfigFile.I
        assert workflow.jobs() == (workflow.job_configure,)

    def test_permissions_job_configure(self) -> None:
        """Check checkout is limited to read-only repository access."""
        assert RepositoryWorkflowConfigFile.I.permissions_job_configure() == {
            "contents": "read",
        }

    def test_stem(self) -> None:
        """Check the reusable workflow file name."""
        assert RepositoryWorkflowConfigFile.I.stem() == "repository"

    def test_step_configure_repository(self) -> None:
        """Check the configuration script receives the repository token."""
        workflow = RepositoryWorkflowConfigFile.I
        step = workflow.step_configure_repository()
        path = ConfigureRepositoryConfigFile.I.path().as_posix()
        assert step["run"] == f"bash {path}"
        assert step["env"]["GH_TOKEN"] == workflow.insert_repo_token()

    def test_steps_configure(self) -> None:
        """Check checkout precedes repository configuration."""
        workflow = RepositoryWorkflowConfigFile.I
        assert workflow.steps_configure() == [
            workflow.step_checkout_repository(),
            workflow.step_configure_repository(),
        ]

    def test_workflow_triggers(self) -> None:
        """Check the workflow declares its required reusable-call secret."""
        workflow = RepositoryWorkflowConfigFile.I
        assert workflow.workflow_triggers() == {
            "workflow_call": {
                "secrets": {
                    "REPO_TOKEN": {"required": True},
                },
            },
        }
