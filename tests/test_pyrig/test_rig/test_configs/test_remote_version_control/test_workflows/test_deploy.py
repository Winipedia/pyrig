"""module."""

from pyrig.rig.configs.remote_version_control.workflows.deploy import (
    DeployWorkflowConfigFile,
)


class TestDeployWorkflowConfigFile:
    """Test class."""

    def test_job(self) -> None:
        """Test method."""

        def job_test() -> None:
            pass

        result = DeployWorkflowConfigFile.I.job(job_func=job_test, steps=[])
        assert len(result) == 1, "Expected job to have one key"
        job_config = next(iter(result.values()))
        expected = "${{ github.event.workflow_run.conclusion == 'success' }}"
        assert job_config["if"] == expected

    def test_stem(self) -> None:
        """Test method."""
        assert DeployWorkflowConfigFile.I.stem() == "deploy"

    def test_job_documentation(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.job_documentation()
        assert len(result) == 1
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name]

    def test_steps_documentation(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.steps_documentation()
        assert len(result) > 0

    def test_workflow_triggers(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.workflow_triggers()
        assert "workflow_dispatch" in result, "Expected 'workflow_dispatch' in triggers"
        assert "workflow_run" in result

    def test_jobs(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.jobs()
        assert len(result) > 0
