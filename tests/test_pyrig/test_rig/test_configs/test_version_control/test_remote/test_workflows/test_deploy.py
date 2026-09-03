"""module."""

from pyrig.rig.configs.version_control.remote.workflows.deploy import (
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
        assert "release" in result, "Expected 'release' in triggers"
        assert result["release"]["types"] == ["published"]
        assert "workflow_run" not in result

    def test_jobs(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.jobs()
        assert len(result) > 0

    def test_step_build_documentation(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.step_build_documentation()
        assert "run" in result, f"Expected 'run' in step, got {result}"

    def test_step_configure_pages(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.step_configure_pages()
        assert "uses" in result, f"Expected 'uses' in step, got {result}"

    def test_step_upload_documentation(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.step_upload_documentation()
        assert "uses" in result, f"Expected 'uses' in step, got {result}"

    def test_step_deploy_documentation(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.step_deploy_documentation()
        assert "uses" in result, f"Expected 'uses' in step, got {result}"

    def test_concurrency_cancel_in_progress(self) -> None:
        """Test method."""
        assert DeployWorkflowConfigFile.I.concurrency_cancel_in_progress() is False
