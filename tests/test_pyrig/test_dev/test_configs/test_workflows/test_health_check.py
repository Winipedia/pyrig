"""module."""

from collections.abc import Callable

import pytest

from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow
from pyrig.utils.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_health_check_workflow(
    config_file_factory: Callable[
        [type[HealthCheckWorkflow]], type[HealthCheckWorkflow]
    ],
) -> type[HealthCheckWorkflow]:
    """Create a test health check workflow class with tmp_path."""
    return config_file_factory(HealthCheckWorkflow)


class TestHealthCheckWorkflow:
    """Test class for HealthCheckWorkflow."""

    def test_get_workflow_triggers(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for get_workflow_triggers."""
        result = my_test_health_check_workflow.get_workflow_triggers()
        assert_with_msg(
            "workflow_dispatch" in result, "Expected 'workflow_dispatch' in triggers"
        )
        assert_with_msg("pull_request" in result, "Expected 'pull_request' in triggers")
        assert_with_msg("schedule" in result, "Expected 'schedule' in triggers")

    def test_get_jobs(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for get_jobs."""
        result = my_test_health_check_workflow.get_jobs()
        assert_with_msg(len(result) > 0, "Expected jobs to be non-empty")

    def test_job_health_check_matrix(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for job_health_check_matrix."""
        result = my_test_health_check_workflow.job_health_check_matrix()
        assert_with_msg(len(result) == 1, "Expected job to have one key")
        job_name = next(iter(result.keys()))
        assert_with_msg("steps" in result[job_name], "Expected 'steps' in job")
        assert_with_msg("strategy" in result[job_name], "Expected 'strategy' in job")
        assert_with_msg("runs-on" in result[job_name], "Expected 'runs-on' in job")

    def test_job_health_check(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for job_health_check."""
        result = my_test_health_check_workflow.job_health_check()
        assert_with_msg(len(result) == 1, "Expected job to have one key")
        job_name = next(iter(result.keys()))
        assert_with_msg("steps" in result[job_name], "Expected 'steps' in job")
        assert_with_msg("needs" in result[job_name], "Expected 'needs' in job")

    def test_steps_health_check_matrix(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for steps_health_check_matrix."""
        result = my_test_health_check_workflow.steps_health_check_matrix()
        assert_with_msg(len(result) > 0, "Expected steps to be non-empty")

    def test_steps_aggregate_matrix_results(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for steps_aggregate_matrix_results."""
        result = my_test_health_check_workflow.steps_aggregate_matrix_results()
        assert_with_msg(len(result) > 0, "Expected steps to be non-empty")

    def test_is_correct(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for is_correct."""
        test_workflow = my_test_health_check_workflow()
        workflow_path = test_workflow.get_path()
        workflow_path.write_text("")
        assert_with_msg(
            test_workflow.is_correct(),
            "Expected workflow to be correct when empty",
        )

        loaded_config = test_workflow.load()
        assert_with_msg(
            loaded_config == HealthCheckWorkflow.EMPTY_CONFIG,
            "Expected empty workflow to have EMPTY_CONFIG after is_correct check",
        )

        proper_config = test_workflow.get_configs()
        test_workflow.dump(proper_config)
        assert_with_msg(
            test_workflow.is_correct(),
            "Expected workflow to be correct with proper config",
        )
