"""module."""

from pyrig.rig.configs.version_control.remote.configure import (
    ConfigureRepositoryConfigFile,
)
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

    def test_job_repository(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.job_repository()
        assert len(result) == 1
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name]
        assert result[job_name]["environment"] == job_name
        assert result[job_name]["permissions"] == {"contents": "read"}

    def test_steps_repository(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.steps_repository()
        assert len(result) > 0

    def test_step_configure_repository(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.step_configure_repository()
        path = ConfigureRepositoryConfigFile.I.path().as_posix()
        assert result["run"] == f"bash {path}"
        assert result["env"]["GH_TOKEN"]

    def test_steps_documentation(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.steps_documentation()
        assert len(result) > 0

    def test_workflow_triggers(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.workflow_triggers()
        assert "workflow_call" in result, "Expected 'workflow_call' in triggers"
        assert result["workflow_call"]["secrets"] == {"REPO_TOKEN": {"required": True}}
        assert "release" not in result

    def test_used_secrets(self) -> None:
        """Test method."""
        assert DeployWorkflowConfigFile.I.used_secrets() == ["REPO_TOKEN"]

    def test_jobs(self) -> None:
        """Test method."""
        result = DeployWorkflowConfigFile.I.jobs()
        assert {"repository", "documentation"} <= set(result)

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

    def test_job(self) -> None:
        """Test method."""
        workflow = DeployWorkflowConfigFile()

        result = workflow.job(self.test_job, steps=[])
        assert len(result) == 1, "Expected job to have one key"
        job_config = next(iter(result.values()))
        assert job_config["environment"] == "test-job"

        result = workflow.job(
            self.test_job,
            environment="custom",
            steps=[],
        )
        job_config = next(iter(result.values()))
        assert job_config["environment"] == "custom"
