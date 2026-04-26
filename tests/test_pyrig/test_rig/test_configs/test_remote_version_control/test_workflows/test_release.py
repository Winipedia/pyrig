"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.remote_version_control.workflows.release import (
    ReleaseWorkflowConfigFile,
)


@pytest.fixture
def my_test_release_workflow(
    config_file_factory: Callable[
        [type[ReleaseWorkflowConfigFile]], type[ReleaseWorkflowConfigFile]
    ],
) -> type[ReleaseWorkflowConfigFile]:
    """Create a test release workflow class with tmp_path."""
    return config_file_factory(ReleaseWorkflowConfigFile)


class TestReleaseWorkflowConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        assert ReleaseWorkflowConfigFile.I.stem() == "release"

    def test_workflow_triggers(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().workflow_triggers()
        assert "workflow_dispatch" in result, "Expected 'workflow_dispatch' in triggers"
        assert "pull_request" not in result

    def test_permissions(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().permissions()
        assert "contents" in result, "Expected 'contents' in permissions"
        assert result["contents"] == "write", "Expected 'contents' to be 'write'"
        assert "actions" in result, "Expected 'actions' in permissions"
        assert result["actions"] == "read", "Expected 'actions' to be 'read'"

    def test_jobs(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().jobs()
        assert len(result) > 0, "Expected jobs to be non-empty"

    def test_job_release(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().job_release()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"

    def test_steps_release(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().steps_release()
        assert len(result) > 0, "Expected steps to be non-empty"
