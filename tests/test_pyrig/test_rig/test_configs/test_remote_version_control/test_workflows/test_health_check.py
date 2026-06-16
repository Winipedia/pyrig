"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.remote_version_control.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)


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

    def test_stem(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile.I.stem() == "health_check"

    def test_cron_schedule(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile().cron_schedule() == (0, 1, "*", "*", "*")

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
        assert "steps" in result[job_name]
        assert "needs" in result[job_name]

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

    def test_step_run_tests(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        step = my_test_health_check_workflow().step_run_tests()
        assert "run" in step
        step = my_test_health_check_workflow().step_run_tests(step={})
        assert "run" in step

        assert "env" not in step

        health_check_step = HealthCheckWorkflowConfigFile.I.step_run_tests()
        expected = {"REPO_TOKEN": "${{ secrets.REPO_TOKEN }}"}  # nosec: B105
        assert health_check_step["env"] == expected

    def test_step_run_pre_commit_hooks(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().step_run_pre_commit_hooks()
        assert "run" in result

    def test_step_run_dependency_audit(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().step_run_dependency_audit()
        assert "run" in result, f"Expected 'run' in step, got {result}"

    def test_step_protect_repository(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().step_protect_repository()
        assert "env" in result, "Expected 'env' in step"

    def test_step_aggregate_jobs(
        self, my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().step_aggregate_jobs()
        assert "name" in result, "Expected 'name' in step"
        assert "run" in result
