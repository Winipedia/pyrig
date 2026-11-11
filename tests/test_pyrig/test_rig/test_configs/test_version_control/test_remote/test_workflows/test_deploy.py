"""Tests for the deployment workflow."""

from pyrig.rig.configs.version_control.remote.workflows.deploy import (
    DeployWorkflowConfigFile,
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
        """Check the base workflow calls."""
        workflow = DeployWorkflowConfigFile.I
        assert workflow.job_repository in workflow.jobs()
        assert workflow.job_documentation in workflow.jobs()

    def test_stem(self) -> None:
        """Check the workflow file stem."""
        assert DeployWorkflowConfigFile.I.stem() == "deploy"

    def test_workflow_triggers(self) -> None:
        """Check the deploy workflow declares the required secret."""
        assert DeployWorkflowConfigFile.I.workflow_triggers() == {
            "workflow_call": {"secrets": {"REPO_TOKEN": {"required": True}}},
        }
