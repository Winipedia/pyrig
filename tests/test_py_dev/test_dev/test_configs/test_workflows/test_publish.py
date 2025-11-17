"""module."""

from collections.abc import Callable

import pytest

from py_dev.dev.configs.workflows.publish import PublishWorkflow
from py_dev.utils.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_publish_workflow(
    config_file_factory: Callable[[type[PublishWorkflow]], type[PublishWorkflow]],
) -> type[PublishWorkflow]:
    """Create a test publish workflow class with tmp_path."""
    return config_file_factory(PublishWorkflow)


class TestPublishWorkflow:
    """Test class for PublishWorkflow."""

    def test_get_workflow_triggers(
        self, my_test_publish_workflow: type[PublishWorkflow]
    ) -> None:
        """Test method for get_workflow_triggers."""
        result = my_test_publish_workflow.get_workflow_triggers()
        assert_with_msg(
            "workflow_dispatch" in result, "Expected 'workflow_dispatch' in triggers"
        )
        assert_with_msg("workflow_run" in result, "Expected 'workflow_run' in triggers")

    def test_get_jobs(self, my_test_publish_workflow: type[PublishWorkflow]) -> None:
        """Test method for get_jobs."""
        result = my_test_publish_workflow.get_jobs()
        assert_with_msg(len(result) > 0, "Expected jobs to be non-empty")

    def test_job_publish(self, my_test_publish_workflow: type[PublishWorkflow]) -> None:
        """Test method for job_publish."""
        result = my_test_publish_workflow.job_publish()
        assert_with_msg(len(result) == 1, "Expected job to have one key")
        job_name = next(iter(result.keys()))
        assert_with_msg("steps" in result[job_name], "Expected 'steps' in job")
        assert_with_msg("if" in result[job_name], "Expected 'if' condition in job")

    def test_steps_publish(
        self, my_test_publish_workflow: type[PublishWorkflow]
    ) -> None:
        """Test method for steps_publish."""
        result = my_test_publish_workflow.steps_publish()
        assert_with_msg(len(result) > 0, "Expected steps to be non-empty")

    def test_is_correct(self, my_test_publish_workflow: type[PublishWorkflow]) -> None:
        """Test method for is_correct."""
        test_workflow = my_test_publish_workflow()
        workflow_path = test_workflow.get_path()
        workflow_path.write_text("")
        assert_with_msg(
            test_workflow.is_correct(),
            "Expected workflow to be correct when empty",
        )

        loaded_config = test_workflow.load()
        assert_with_msg(
            loaded_config == PublishWorkflow.EMPTY_CONFIG,
            "Expected empty workflow to have EMPTY_CONFIG after is_correct check",
        )

        proper_config = test_workflow.get_configs()
        test_workflow.dump(proper_config)
        assert_with_msg(
            test_workflow.is_correct(),
            "Expected workflow to be correct with proper config",
        )
