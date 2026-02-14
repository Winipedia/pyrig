"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.workflows.deploy import DeployWorkflow


@pytest.fixture
def my_test_deploy_workflow(
    config_file_factory: Callable[[type[DeployWorkflow]], type[DeployWorkflow]],
) -> type[DeployWorkflow]:
    """Create a test deploy workflow class with tmp_path."""
    return config_file_factory(DeployWorkflow)


class TestDeployWorkflow:
    """Test class."""

    def test_job_deploy_documentation(self) -> None:
        """Test method."""
        result = DeployWorkflow.job_deploy_documentation()
        assert len(result) == 1, f"Expected job to have one key, got {result}"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"

    def test_steps_deploy_documentation(self) -> None:
        """Test method."""
        result = DeployWorkflow.steps_deploy_documentation()
        assert len(result) > 0, f"Expected steps to be non-empty, got {result}"

    def test_workflow_triggers(
        self, my_test_deploy_workflow: type[DeployWorkflow]
    ) -> None:
        """Test method."""
        result = my_test_deploy_workflow.workflow_triggers()
        assert "workflow_dispatch" in result, "Expected 'workflow_dispatch' in triggers"
        assert "workflow_run" in result, "Expected 'workflow_run' in triggers"

    def test_jobs(self, my_test_deploy_workflow: type[DeployWorkflow]) -> None:
        """Test method."""
        result = my_test_deploy_workflow.jobs()
        assert len(result) > 0, "Expected jobs to be non-empty"

    def test_job_publish_package(
        self, my_test_deploy_workflow: type[DeployWorkflow]
    ) -> None:
        """Test method."""
        result = my_test_deploy_workflow.job_publish_package()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"
        assert "if" in result[job_name], "Expected 'if' condition in job"

    def test_steps_publish_package(
        self, my_test_deploy_workflow: type[DeployWorkflow]
    ) -> None:
        """Test method."""
        result = my_test_deploy_workflow.steps_publish_package()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_is_correct(self, my_test_deploy_workflow: type[DeployWorkflow]) -> None:
        """Test method."""
        my_test_deploy_workflow.validate()
        workflow_path = my_test_deploy_workflow.path()
        workflow_path.write_text("")
        assert my_test_deploy_workflow.is_correct(), (
            "Expected workflow to be correct when empty"
        )

        proper_config = my_test_deploy_workflow.configs()
        my_test_deploy_workflow.dump(proper_config)
        assert my_test_deploy_workflow.is_correct(), (
            "Expected workflow to be correct with proper config"
        )
