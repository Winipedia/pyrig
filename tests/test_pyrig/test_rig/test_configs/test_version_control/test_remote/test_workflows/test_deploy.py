"""Tests for the deployment workflow."""

from pyrig.rig.configs.version_control.remote.workflows.deploy import (
    DeployWorkflowConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.documentation import (
    DocumentationWorkflowConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.repository import (
    RepositoryWorkflowConfigFile,
)


class TestDeployWorkflowConfigFile:
    """Tests for the deployment workflow calls."""

    def test_concurrency_cancel_in_progress(self) -> None:
        """Check deployments are not cancelled while publishing."""
        assert DeployWorkflowConfigFile.I.concurrency_cancel_in_progress() is False

    def test_job_documentation(self) -> None:
        """Check the documentation call forwards its permissions and secrets."""
        job = DeployWorkflowConfigFile.I.job_documentation()
        assert job["job_id"] == "documentation"
        assert job["uses"] == "$/.github/workflows/documentation.yml"
        assert job["permissions"] == {
            "contents": "read",
            "id-token": "write",
            "pages": "write",
        }
        assert job["secrets"] == {"REPO_TOKEN": "${{ secrets.REPO_TOKEN }}"}
        assert "runs-on" not in job
        assert "environment" not in job
        assert "steps" not in job

    def test_job_repository(self) -> None:
        """Check the repository workflow call."""
        job = DeployWorkflowConfigFile.I.job_repository()
        assert job["job_id"] == "repository"
        assert job["uses"] == "$/.github/workflows/repository.yml"
        assert job["permissions"] == {"contents": "read"}
        assert job["secrets"] == {"REPO_TOKEN": "${{ secrets.REPO_TOKEN }}"}

    def test_jobs(self) -> None:
        """Check the base calls are included in the persisted deploy workflow."""
        workflow = DeployWorkflowConfigFile.I
        assert {workflow.job_repository, workflow.job_documentation} <= set(
            workflow.jobs(),
        )
        generated = workflow.jobs_configs()
        persisted = workflow.load()["jobs"]
        for job_id in ("repository", "documentation"):
            assert persisted[job_id] == generated[job_id]
        assert "build-documentation" not in persisted
        assert "deploy-documentation" not in persisted
        assert RepositoryWorkflowConfigFile.I.load()["jobs"] == (
            RepositoryWorkflowConfigFile.I.jobs_configs()
        )
        assert DocumentationWorkflowConfigFile.I.load()["jobs"] == (
            DocumentationWorkflowConfigFile.I.jobs_configs()
        )

    def test_stem(self) -> None:
        """Check the workflow file stem."""
        assert DeployWorkflowConfigFile.I.stem() == "deploy"

    def test_used_secrets(self) -> None:
        """Check secrets are discovered through the nested calls."""
        assert DeployWorkflowConfigFile.I.used_secrets() == ["REPO_TOKEN"]

    def test_workflow_triggers(self) -> None:
        """Check the deploy workflow declares the required secret."""
        assert DeployWorkflowConfigFile.I.workflow_triggers() == {
            "workflow_call": {"secrets": {"REPO_TOKEN": {"required": True}}},
        }
