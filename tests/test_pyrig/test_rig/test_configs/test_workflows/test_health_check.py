"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.workflows.health_check import HealthCheckWorkflowConfigFile


@pytest.fixture
def my_test_health_check_workflow(
    config_file_factory: Callable[
        [type[HealthCheckWorkflowConfigFile]], type[HealthCheckWorkflowConfigFile]
    ],
) -> type[HealthCheckWorkflowConfigFile]:
    """Create a test health check workflow class with tmp_path."""
    return config_file_factory(HealthCheckWorkflowConfigFile)


class TestHealthCheckWorkflowConfigFile:
    """Test class."""

    def test_job_health_checks(self) -> None:
        """Test method."""
        result = HealthCheckWorkflowConfigFile.I.job_health_checks()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"

    def test_steps_health_checks(self) -> None:
        """Test method."""
        result = HealthCheckWorkflowConfigFile.I.steps_health_checks()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_staggered_cron(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().staggered_cron()
        assert len(result) > 0, "Expected cron to be non-empty"

    def test_dependency_offset(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().dependency_offset()
        assert result >= 0, "Expected offset to be non-negative"

    def test_workflow_triggers(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().workflow_triggers()
        assert "workflow_dispatch" in result, "Expected 'workflow_dispatch' in triggers"
        assert "pull_request" in result, "Expected 'pull_request' in triggers"
        assert "schedule" in result, "Expected 'schedule' in triggers"

    def test_jobs(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().jobs()
        assert len(result) > 0, "Expected jobs to be non-empty"

    def test_job_matrix_health_checks(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().job_matrix_health_checks()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"
        assert "strategy" in result[job_name], "Expected 'strategy' in job"
        assert "runs-on" in result[job_name], "Expected 'runs-on' in job"

    def test_job_health_check(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().job_health_check()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"
        assert "needs" in result[job_name], "Expected 'needs' in job"

    def test_steps_matrix_health_checks(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().steps_matrix_health_checks()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_steps_aggregate_jobs(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().steps_aggregate_jobs()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_is_correct(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        my_test_health_check_workflow().validate()
        workflow_path = my_test_health_check_workflow().path()
        workflow_path.write_text("")
        assert my_test_health_check_workflow().is_correct(), (
            "Expected workflow to be correct when empty"
        )

        proper_config = my_test_health_check_workflow().configs()
        my_test_health_check_workflow().dump(proper_config)
        assert my_test_health_check_workflow().is_correct(), (
            "Expected workflow to be correct with proper config"
        )
