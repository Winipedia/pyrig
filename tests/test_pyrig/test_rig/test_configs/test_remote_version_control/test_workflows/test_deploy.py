"""module."""

from pyrig.rig.configs.remote_version_control.workflows.deploy import (
    DeployWorkflowConfigFile,
)


class TestDeployWorkflowConfigFile:
    """Test class."""

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
