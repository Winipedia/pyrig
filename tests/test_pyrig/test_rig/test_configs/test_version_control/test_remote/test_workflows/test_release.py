"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.version_control.remote.workflows.release import (
    ReleaseWorkflowConfigFile,
)


@pytest.fixture
def my_test_release_workflow(
    config_file_factory: Callable[
        [type[ReleaseWorkflowConfigFile]],
        type[ReleaseWorkflowConfigFile],
    ],
) -> type[ReleaseWorkflowConfigFile]:
    """Create a test release workflow class with tmp_path."""
    return config_file_factory(ReleaseWorkflowConfigFile)


class TestReleaseWorkflowConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        assert ReleaseWorkflowConfigFile().stem() == "release"

    def test_workflow_triggers(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().workflow_triggers()
        assert "push" in result, "Expected 'push' in triggers"
        assert "workflow_run" not in result
        assert "workflow_dispatch" not in result
        assert "pull_request" not in result

    def test_jobs(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().jobs()
        assert len(result) > 0, "Expected jobs to be non-empty"

    def test_job_health_check(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().job_health_check()
        assert len(result) == 1, "Expected job to have one key"
        job_config = next(iter(result.values()))
        assert job_config["uses"] == "$/.github/workflows/health_check.yml"
        assert job_config["secrets"] == {
            "CODECOV_TOKEN": "${{ secrets.CODECOV_TOKEN }}",
        }
        assert "environment" not in job_config

    def test_job_publish(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().job_publish()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"
        assert "needs" in result[job_name], "Expected 'needs' in job"
        assert "environment" not in result[job_name]

    def test_job_deploy(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().job_deploy()
        assert len(result) == 1, "Expected job to have one key"
        job_config = next(iter(result.values()))
        assert job_config["uses"] == "$/.github/workflows/deploy.yml"
        assert job_config["secrets"] == {"REPO_TOKEN": "${{ secrets.REPO_TOKEN }}"}
        assert "needs" in job_config, "Expected 'needs' in job"
        assert "environment" not in job_config

    def test_steps_publish(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().steps_publish()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_step_create_release(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().step_create_release()
        assert "gh" in result["run"]
        assert "release" in result["run"]
        assert "create" in result["run"]
        assert "--title=" in result["run"]
        assert "--generate-notes" in result["run"]
        assert result["env"]["GH_TOKEN"]

    def test_concurrency_cancel_in_progress(self) -> None:
        """Test method."""
        assert ReleaseWorkflowConfigFile.I.concurrency_cancel_in_progress() is False
