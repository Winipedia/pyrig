"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.workflows.release import ReleaseWorkflow


@pytest.fixture
def my_test_release_workflow(
    config_file_factory: Callable[[type[ReleaseWorkflow]], type[ReleaseWorkflow]],
) -> type[ReleaseWorkflow]:
    """Create a test release workflow class with tmp_path."""
    return config_file_factory(ReleaseWorkflow)


class TestReleaseWorkflow:
    """Test class."""

    def test_get_workflow_triggers(
        self, my_test_release_workflow: type[ReleaseWorkflow]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow.get_workflow_triggers()
        assert "workflow_dispatch" in result, "Expected 'workflow_dispatch' in triggers"
        assert "pull_request" not in result

    def test_get_permissions(
        self, my_test_release_workflow: type[ReleaseWorkflow]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow.get_permissions()
        assert "contents" in result, "Expected 'contents' in permissions"
        assert result["contents"] == "write", "Expected 'contents' to be 'write'"
        assert "actions" in result, "Expected 'actions' in permissions"
        assert result["actions"] == "read", "Expected 'actions' to be 'read'"

    def test_get_jobs(self, my_test_release_workflow: type[ReleaseWorkflow]) -> None:
        """Test method."""
        result = my_test_release_workflow.get_jobs()
        assert len(result) > 0, "Expected jobs to be non-empty"

    def test_job_release(self, my_test_release_workflow: type[ReleaseWorkflow]) -> None:
        """Test method."""
        result = my_test_release_workflow.job_release()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"

    def test_steps_release(
        self, my_test_release_workflow: type[ReleaseWorkflow]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow.steps_release()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_is_correct(self, my_test_release_workflow: type[ReleaseWorkflow]) -> None:
        """Test method."""
        test_workflow = my_test_release_workflow()
        workflow_path = test_workflow.path()
        workflow_path.write_text("")
        assert test_workflow.is_correct(), "Expected workflow to be correct when empty"

        proper_config = test_workflow.configs()
        test_workflow.dump(proper_config)
        assert test_workflow.is_correct(), (
            "Expected workflow to be correct with proper config"
        )
