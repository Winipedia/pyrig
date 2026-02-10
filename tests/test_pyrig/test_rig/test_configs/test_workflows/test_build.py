"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.workflows.build import BuildWorkflow


@pytest.fixture
def my_test_build_workflow(
    config_file_factory: Callable[[type[BuildWorkflow]], type[BuildWorkflow]],
) -> type[BuildWorkflow]:
    """Create a test build workflow class with tmp_path."""
    return config_file_factory(BuildWorkflow)


class TestBuildWorkflow:
    """Test class."""

    def test_job_build_container_image(
        self, my_test_build_workflow: type[BuildWorkflow]
    ) -> None:
        """Test method."""
        result = my_test_build_workflow.job_build_container_image()
        assert len(result) == 1, f"Expected job to have one key, got {result}"

    def test_steps_build_container_image(
        self, my_test_build_workflow: type[BuildWorkflow]
    ) -> None:
        """Test method."""
        result = my_test_build_workflow.steps_build_container_image()
        assert len(result) > 0, f"Expected some steps, got {result}"

    def test_get_workflow_triggers(
        self, my_test_build_workflow: type[BuildWorkflow]
    ) -> None:
        """Test method for get_workflow_triggers."""
        result = my_test_build_workflow.get_workflow_triggers()
        assert "workflow_dispatch" in result, "Expected 'workflow_dispatch' in triggers"
        assert "workflow_run" in result, "Expected 'workflow_run' in triggers"
        assert "pull_request" not in result

    def test_get_jobs(self, my_test_build_workflow: type[BuildWorkflow]) -> None:
        """Test method for get_jobs."""
        result = my_test_build_workflow.get_jobs()
        assert len(result) > 0, "Expected jobs to be non-empty"

    def test_job_build_artifacts(
        self, my_test_build_workflow: type[BuildWorkflow]
    ) -> None:
        """Test method for job_build."""
        result = my_test_build_workflow.job_build_artifacts()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"
        assert "strategy" in result[job_name], "Expected 'strategy' in job"
        assert "runs-on" in result[job_name], "Expected 'runs-on' in job"

    def test_steps_build_artifacts(
        self, my_test_build_workflow: type[BuildWorkflow]
    ) -> None:
        """Test method for steps_build."""
        result = my_test_build_workflow.steps_build_artifacts()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_is_correct(self, my_test_build_workflow: type[BuildWorkflow]) -> None:
        """Test method for is_correct."""
        test_workflow = my_test_build_workflow()
        workflow_path = test_workflow.get_path()
        workflow_path.write_text("")
        assert test_workflow.is_correct(), "Expected workflow to be correct when empty"

        proper_config = test_workflow.get_configs()
        test_workflow.dump(proper_config)
        assert test_workflow.is_correct(), (
            "Expected workflow to be correct with proper config"
        )
