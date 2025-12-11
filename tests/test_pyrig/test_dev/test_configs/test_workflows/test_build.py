"""module."""

from collections.abc import Callable

import pytest

from pyrig.dev.configs.workflows.build import BuildWorkflow
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_build_workflow(
    config_file_factory: Callable[[type[BuildWorkflow]], type[BuildWorkflow]],
) -> type[BuildWorkflow]:
    """Create a test build workflow class with tmp_path."""
    return config_file_factory(BuildWorkflow)


class TestBuildWorkflow:
    """Test class."""

    def test_get_workflow_triggers(
        self, my_test_build_workflow: type[BuildWorkflow]
    ) -> None:
        """Test method for get_workflow_triggers."""
        result = my_test_build_workflow.get_workflow_triggers()
        assert_with_msg(
            "workflow_dispatch" in result, "Expected 'workflow_dispatch' in triggers"
        )
        assert_with_msg("workflow_run" in result, "Expected 'workflow_run' in triggers")
        assert "pull_request" not in result

    def test_get_jobs(self, my_test_build_workflow: type[BuildWorkflow]) -> None:
        """Test method for get_jobs."""
        result = my_test_build_workflow.get_jobs()
        assert_with_msg(len(result) > 0, "Expected jobs to be non-empty")

    def test_job_build(self, my_test_build_workflow: type[BuildWorkflow]) -> None:
        """Test method for job_build."""
        result = my_test_build_workflow.job_build()
        assert_with_msg(len(result) == 1, "Expected job to have one key")
        job_name = next(iter(result.keys()))
        assert_with_msg("steps" in result[job_name], "Expected 'steps' in job")
        assert_with_msg("strategy" in result[job_name], "Expected 'strategy' in job")
        assert_with_msg("runs-on" in result[job_name], "Expected 'runs-on' in job")

    def test_steps_build(self, my_test_build_workflow: type[BuildWorkflow]) -> None:
        """Test method for steps_build."""
        result = my_test_build_workflow.steps_build()
        assert_with_msg(len(result) > 0, "Expected steps to be non-empty")

    def test_is_correct(self, my_test_build_workflow: type[BuildWorkflow]) -> None:
        """Test method for is_correct."""
        test_workflow = my_test_build_workflow()
        workflow_path = test_workflow.get_path()
        workflow_path.write_text("")
        assert_with_msg(
            test_workflow.is_correct(),
            "Expected workflow to be correct when empty",
        )

        proper_config = test_workflow.get_configs()
        test_workflow.dump(proper_config)
        assert_with_msg(
            test_workflow.is_correct(),
            "Expected workflow to be correct with proper config",
        )
