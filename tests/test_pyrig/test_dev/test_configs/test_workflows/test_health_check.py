"""module."""

from collections.abc import Callable

import pytest

from pyrig.dev.configs.workflows.health_check import HealthCheckWorkflow


@pytest.fixture
def my_test_health_check_workflow(
    config_file_factory: Callable[
        [type[HealthCheckWorkflow]], type[HealthCheckWorkflow]
    ],
) -> type[HealthCheckWorkflow]:
    """Create a test health check workflow class with tmp_path."""
    return config_file_factory(HealthCheckWorkflow)


class TestHealthCheckWorkflow:
    """Test class."""

    def test_job_protect_repository(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow.job_protect_repository()
        assert isinstance(result, dict), "Expected dict"

    def test_steps_protect_repository(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow.steps_protect_repository()
        assert isinstance(result, list), "Expected list"

    def test_get_staggered_cron(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow.get_staggered_cron()
        assert len(result) > 0, "Expected cron to be non-empty"

    def test_get_dependency_offset(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow.get_dependency_offset()
        assert result >= 0, "Expected offset to be non-negative"

    def test_get_workflow_triggers(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for get_workflow_triggers."""
        result = my_test_health_check_workflow.get_workflow_triggers()
        assert "workflow_dispatch" in result, "Expected 'workflow_dispatch' in triggers"
        assert "pull_request" in result, "Expected 'pull_request' in triggers"
        assert "schedule" in result, "Expected 'schedule' in triggers"

    def test_get_jobs(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for get_jobs."""
        result = my_test_health_check_workflow.get_jobs()
        assert len(result) > 0, "Expected jobs to be non-empty"

    def test_job_health_check_matrix(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for job_health_check_matrix."""
        result = my_test_health_check_workflow.job_health_check_matrix()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"
        assert "strategy" in result[job_name], "Expected 'strategy' in job"
        assert "runs-on" in result[job_name], "Expected 'runs-on' in job"

    def test_job_health_check(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for job_health_check."""
        result = my_test_health_check_workflow.job_health_check()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"
        assert "needs" in result[job_name], "Expected 'needs' in job"

    def test_steps_health_check_matrix(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for steps_health_check_matrix."""
        result = my_test_health_check_workflow.steps_health_check_matrix()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_steps_aggregate_matrix_results(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for steps_aggregate_matrix_results."""
        result = my_test_health_check_workflow.steps_aggregate_matrix_results()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_is_correct(
        self, my_test_health_check_workflow: type[HealthCheckWorkflow]
    ) -> None:
        """Test method for is_correct."""
        test_workflow = my_test_health_check_workflow()
        workflow_path = test_workflow.get_path()
        workflow_path.write_text("")
        assert test_workflow.is_correct(), "Expected workflow to be correct when empty"

        proper_config = test_workflow.get_configs()
        test_workflow.dump(proper_config)
        assert test_workflow.is_correct(), (
            "Expected workflow to be correct with proper config"
        )
