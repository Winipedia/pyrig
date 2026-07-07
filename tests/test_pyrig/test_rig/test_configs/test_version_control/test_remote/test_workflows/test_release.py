"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.version_control.remote.workflows.release import (
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

    def test_step_apply_repository_settings(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        step = my_test_release_workflow().step_apply_repository_settings()
        assert "run" in step
        assert "env" in step

    def test_step_apply_rulesets(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        step = my_test_release_workflow().step_apply_rulesets()
        assert "run" in step
        assert "env" in step

    def test_steps_configure_repository(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        workflow = my_test_release_workflow()
        step_settings, step_rulesets = workflow.steps_configure_repository()
        assert "run" in step_settings
        assert "env" in step_settings
        assert "run" in step_rulesets
        assert "env" in step_rulesets

    def test_job(self) -> None:
        """Test method."""
        result = ReleaseWorkflowConfigFile.I.job(self.test_job, steps=[])
        assert len(result) == 1, "Expected job to have one key"
        job_config = next(iter(result.values()))
        expected = (
            "${{ github.event.workflow_run.conclusion == 'success' "
            "&& github.event.workflow_run.event == 'push' }}"
        )
        assert job_config["if"] == expected

    def test_stem(self) -> None:
        """Test method."""
        assert ReleaseWorkflowConfigFile.I.stem() == "release"

    def test_workflow_triggers(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().workflow_triggers()
        assert "workflow_run" in result, "Expected 'workflow_run' in triggers"
        assert "workflow_dispatch" not in result
        assert "pull_request" not in result

    def test_jobs(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().jobs()
        assert len(result) > 0, "Expected jobs to be non-empty"

    def test_job_publish(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().job_publish()
        assert len(result) == 1, "Expected job to have one key"
        job_name = next(iter(result.keys()))
        assert "steps" in result[job_name], "Expected 'steps' in job"

    def test_steps_publish(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().steps_publish()
        assert len(result) > 0, "Expected steps to be non-empty"

    def test_step_create_tag(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        step = my_test_release_workflow().step_create_tag()
        assert "run" in step

    def test_step_push_tag(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        step = my_test_release_workflow().step_push_tag()
        assert "run" in step

    def test_step_extract_version(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().step_extract_version()
        assert "run" in result

    def test_step_build_changelog(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().step_build_changelog()
        assert "uses" in result, "Expected 'uses' in step"

    def test_step_create_release(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().step_create_release()
        assert "uses" in result, "Expected 'uses' in step"

    def test_insert_version_from_extract_version_step(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().insert_version_from_extract_version_step()
        assert "steps.extract-version.outputs.version" in result

    def test_insert_changelog(
        self, my_test_release_workflow: type[ReleaseWorkflowConfigFile]
    ) -> None:
        """Test method."""
        result = my_test_release_workflow().insert_changelog()
        assert "steps.build-changelog.outputs.changelog" in result
