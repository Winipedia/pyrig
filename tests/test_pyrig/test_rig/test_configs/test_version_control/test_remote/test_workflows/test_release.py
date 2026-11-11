"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.version_control.remote.workflows.release import (
    ReleaseWorkflowConfigFile,
)


class TestReleaseWorkflowConfigFile:
    """Test class."""

    def test_concurrency_cancel_in_progress(self) -> None:
        """Test method."""
        assert ReleaseWorkflowConfigFile.I.concurrency_cancel_in_progress() is False

    def test_job_deploy(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().job_deploy()
        assert result["job_id"] == "deploy"
        assert result["uses"] == "$/.github/workflows/deploy.yml"
        assert result["secrets"] == {"REPO_TOKEN": "${{ secrets.REPO_TOKEN }}"}
        assert "needs" in result, "Expected 'needs' in job"
        assert "environment" not in result

    def test_job_deploy_needs(self) -> None:
        """Test method."""
        assert ReleaseWorkflowConfigFile.I.job_deploy_needs() == (
            ReleaseWorkflowConfigFile.I.job_publish,
        )

    def test_job_health_check(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().job_health_check()
        assert result["job_id"] == "health-check"
        assert result["uses"] == "$/.github/workflows/health-check.yml"
        assert result["permissions"] == {
            "actions": "read",
            "contents": "read",
            "id-token": "write",
            "security-events": "write",
        }
        assert "secrets" not in result
        assert "environment" not in result

    def test_job_publish(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().job_publish()
        assert result["job_id"] == "publish"
        assert "steps" in result, "Expected 'steps' in job"
        assert "needs" in result, "Expected 'needs' in job"
        assert "environment" not in result

    def test_job_publish_needs(self) -> None:
        """Test method."""
        assert ReleaseWorkflowConfigFile.I.job_publish_needs() == (
            ReleaseWorkflowConfigFile.I.job_health_check,
        )

    def test_job_publish_permissions(self) -> None:
        """Test method."""
        assert ReleaseWorkflowConfigFile.I.job_publish_permissions() == {
            "contents": "write",
        }

    def test_jobs(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_release_workflow()
        assert workflow.jobs() == (
            workflow.job_health_check,
            workflow.job_publish,
            workflow.job_deploy,
        )

    def test_stem(self) -> None:
        """Test method."""
        assert ReleaseWorkflowConfigFile.I.stem() == "release"

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

    def test_steps_publish(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().steps_publish()
        assert len(result) > 0, "Expected steps to be non-empty"

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


@pytest.fixture
def my_test_release_workflow(
    config_file_factory: Callable[
        [type[ReleaseWorkflowConfigFile]],
        type[ReleaseWorkflowConfigFile],
    ],
) -> type[ReleaseWorkflowConfigFile]:
    """Create a test release workflow class with tmp_path."""
    return config_file_factory(ReleaseWorkflowConfigFile)
