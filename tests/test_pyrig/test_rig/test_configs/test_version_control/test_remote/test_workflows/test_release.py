"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.version_control.remote.configure import (
    ConfigureRepositoryConfigFile,
)
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

    def test_step_configure_repository(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        step = my_test_release_workflow().step_configure_repository()
        path = ConfigureRepositoryConfigFile().path().as_posix()
        assert step["run"] == f"bash {path}"
        assert step["env"]["GH_TOKEN"]

    def test_job(self) -> None:
        """Test method."""
        result = ReleaseWorkflowConfigFile().job(self.test_job, steps=[])
        assert len(result) == 1, "Expected job to have one key"
        job_config = next(iter(result.values()))
        expected = (
            "github.event.workflow_run.conclusion == 'success' &&\n"
            "github.event.workflow_run.event == 'push'"
        )
        assert job_config["if"] == expected

    def test_stem(self) -> None:
        """Test method."""
        assert ReleaseWorkflowConfigFile().stem() == "release"

    def test_workflow_triggers(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().workflow_triggers()
        assert "workflow_run" in result, "Expected 'workflow_run' in triggers"
        assert "workflow_dispatch" not in result
        assert "pull_request" not in result

    def test_jobs(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().jobs()
        assert len(result) > 0, "Expected jobs to be non-empty"

    def test_job_publish(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().job_publish()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"

    def test_steps_publish(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().steps_publish()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_step_create_tag(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        step = my_test_release_workflow().step_create_tag()
        assert "run" in step

    def test_step_push_tag(
        self,
        my_test_release_workflow: type[ReleaseWorkflowConfigFile],
    ) -> None:
        """Test method."""
        step = my_test_release_workflow().step_push_tag()
        assert "run" in step

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
