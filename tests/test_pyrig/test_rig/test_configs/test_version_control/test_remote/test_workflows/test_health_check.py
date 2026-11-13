"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)


class TestHealthCheckWorkflowConfigFile:
    """Test class."""

    def test_cron_schedule(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile().cron_schedule() == (0, 1, "*", "*", "*")

    def test_job_health_check(
        self,
        my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().job_health_check()
        assert result["job_id"] == "health-check"
        assert "steps" in result, "Expected 'steps' in job"
        assert result["needs"] == ["health-checks", "matrix-health-checks"]

    def test_job_health_check_needs(self) -> None:
        """Test method."""
        workflow = HealthCheckWorkflowConfigFile.I
        assert workflow.job_health_check_needs() == workflow.jobs_health_check()

    def test_job_health_checks(self) -> None:
        """Test method."""
        result = HealthCheckWorkflowConfigFile().job_health_checks()
        assert result["job_id"] == "health-checks"
        assert "steps" in result, "Expected 'steps' in job"

    def test_job_matrix_health_checks(
        self,
        my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().job_matrix_health_checks()
        assert result["job_id"] == "matrix-health-checks"
        assert "steps" in result, "Expected 'steps' in job"
        assert "strategy" in result, "Expected 'strategy' in job"
        assert "runs-on" in result, "Expected 'runs-on' in job"

    def test_jobs(
        self,
        my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_health_check_workflow()
        assert workflow.jobs() == (
            workflow.job_health_checks,
            workflow.job_matrix_health_checks,
            workflow.job_health_check,
        )

    def test_jobs_health_check(self) -> None:
        """Test method."""
        workflow = HealthCheckWorkflowConfigFile()
        assert workflow.jobs_health_check() == (
            workflow.job_health_checks,
            workflow.job_matrix_health_checks,
        )

    def test_permissions_job_health_checks(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile().permissions_job_health_checks() == {
            "contents": "read",
        }

    def test_permissions_job_matrix_health_checks(self) -> None:
        """Test method."""
        assert (
            HealthCheckWorkflowConfigFile().permissions_job_matrix_health_checks()
            == {"contents": "read"}
        )

    def test_stem(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile.I.stem() == "health-check"

    def test_step_aggregate_jobs(
        self,
        my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().step_aggregate_jobs()
        assert "name" in result, "Expected 'name' in step"
        assert "run" in result

    def test_step_run_tests(
        self,
        my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile],
    ) -> None:
        """Test method."""
        step = my_test_health_check_workflow().step_run_tests()
        assert "run" in step
        assert "env" not in step

    def test_step_run_version_control_hooks(
        self,
        my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().step_run_version_control_hooks()
        assert "run" in result
        assert result["env"] == {"GH_TOKEN": "${{ secrets.GITHUB_TOKEN }}"}

    def test_steps_aggregate_jobs(
        self,
        my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().steps_aggregate_jobs()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_steps_health_checks(self) -> None:
        """Test method."""
        result = HealthCheckWorkflowConfigFile().steps_health_checks()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_steps_matrix_health_checks(
        self,
        my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().steps_matrix_health_checks()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_workflow_triggers(
        self,
        my_test_health_check_workflow: type[HealthCheckWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_health_check_workflow().workflow_triggers()
        assert "workflow_dispatch" in result, "Expected 'workflow_dispatch' in triggers"
        assert "pull_request" in result, "Expected 'pull_request' in triggers"
        assert "schedule" in result, "Expected 'schedule' in triggers"
        assert "workflow_call" in result, "Expected 'workflow_call' in triggers"
        assert "push" not in result, "Expected 'push' not in triggers"


@pytest.fixture
def my_test_health_check_workflow(
    config_file_factory: Callable[
        [type[HealthCheckWorkflowConfigFile]],
        type[HealthCheckWorkflowConfigFile],
    ],
) -> type[HealthCheckWorkflowConfigFile]:
    """Create a test health check workflow class with tmp_path."""
    return config_file_factory(HealthCheckWorkflowConfigFile)
