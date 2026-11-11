"""module."""

import io
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from typing import Any, override

import pytest
from ruamel.yaml.comments import CommentedMap

from pyrig.core.resources import resource_content
from pyrig.core.strings import read_text_utf8
from pyrig.core.subprocesses import Args
from pyrig.rig import resources
from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.configs.version_control.remote.workflows.deploy import (
    DeployWorkflowConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.release import (
    ReleaseWorkflowConfigFile,
)


class TestWorkflowConfigFile:
    """Test class."""

    def test__configs(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().configs()
        assert "name" in result
        assert "on" in result
        assert "concurrency" in result
        assert "jobs" in result
        assert "permissions" in result
        assert "defaults" not in result

    def test_action_checkout(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        assert workflow.action_checkout() == tuple(
            resource_content(
                "ACTION_CHECKOUT",
                resources,
            ).splitlines(),
        )

        action, ref, tag = HealthCheckWorkflowConfigFile.I.action_checkout()
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(
            HealthCheckWorkflowConfigFile.I.path(),
        )

    def test_action_download_artifact(self) -> None:
        """Test method."""
        assert DeployWorkflowConfigFile.I.action_download_artifact() == tuple(
            resource_content("ACTION_DOWNLOAD_ARTIFACT", resources).splitlines(),
        )

        action, ref, tag = DeployWorkflowConfigFile.I.action_download_artifact()
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(
            DeployWorkflowConfigFile.I.path(),
        )

    def test_action_from_resource(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        assert workflow.action_from_resource(
            workflow.action_checkout,
            resources,
        ) == tuple(
            resource_content("ACTION_CHECKOUT", resources).splitlines(),
        )

    def test_action_ref(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        assert (
            workflow.action_ref("actions/checkout", default="default-sha")
            == "default-sha"
        )

        workflow.create_file()
        custom_configs = {
            "name": "Test",
            "on": {},
            "jobs": {
                "test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout",
                            "id": "checkout",
                            "uses": "actions/checkout@custom-ref-123",
                        },
                    ],
                },
            },
        }
        workflow.dump(custom_configs)
        assert (
            workflow.action_ref("actions/checkout", default="default-sha")
            == "custom-ref-123"
        )
        assert (
            workflow.action_ref("astral-sh/setup-uv", default="default-uv")
            == "default-uv"
        )

    def test_action_setup_uv(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        assert workflow.action_setup_uv() == tuple(
            resource_content(
                "ACTION_SETUP_UV",
                resources,
            ).splitlines(),
        )

        action, ref, tag = HealthCheckWorkflowConfigFile.I.action_setup_uv()
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(
            HealthCheckWorkflowConfigFile.I.path(),
        )

    def test_action_upload_artifact(self) -> None:
        """Test method."""
        assert DeployWorkflowConfigFile.I.action_upload_artifact() == tuple(
            resource_content("ACTION_UPLOAD_ARTIFACT", resources).splitlines(),
        )

        action, ref, tag = DeployWorkflowConfigFile.I.action_upload_artifact()
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(
            DeployWorkflowConfigFile.I.path(),
        )

    def test_assign_command_substitution_output_var(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert (
            my_test_workflow().assign_command_substitution_output_var(
                "name",
                Args("echo", "value"),
            )
            == 'NAME="$(echo value)"\necho name="${NAME}" >> "${GITHUB_OUTPUT}"'
        )

    def test_assign_output_var(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert (
            my_test_workflow().assign_output_var("NAME", "value")
            == 'echo name=value >> "${GITHUB_OUTPUT}"'
        )

    def test_concurrency(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        workflow = my_test_workflow()
        result = workflow.concurrency()
        assert result["group"] == (
            f"{workflow.workflow_name()}-${{{{ github.workflow }}}}-"
            "${{ github.ref }}"
        )
        assert result["cancel-in-progress"] is True

    def test_concurrency_cancel_in_progress(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert my_test_workflow().concurrency_cancel_in_progress() is True

    def test_documented_permissions(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        result = workflow.documented_permissions(
            {"contents": "read", "pages": "write"},
        )

        assert isinstance(result, CommentedMap)
        assert result == {"contents": "read", "pages": "write"}

        buffer = io.StringIO()
        workflow.dumper().dump(result, buffer)
        dumped = buffer.getvalue()
        assert '"contents": "read"\n' in dumped
        assert f'"pages": "write"  # {workflow.permission_comment()}' in dumped

        # No entry needs a comment.
        undocumented = workflow.documented_permissions({"contents": "read"})
        assert isinstance(undocumented, CommentedMap)
        buffer_undocumented = io.StringIO()
        workflow.dumper().dump(undocumented, buffer_undocumented)
        assert "#" not in buffer_undocumented.getvalue()

    def test_github_token_var(self) -> None:
        """Test method."""
        assert (
            HealthCheckWorkflowConfigFile.I.github_token_var() == "secrets.GITHUB_TOKEN"
        )

    def test_id_from_method(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().id_from_method(
            self.test_id_from_method,
            prefix="test",
        )
        assert result == "id-from-method"

    def test_insert_command_substitution(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert (
            my_test_workflow().insert_command_substitution("some command")
            == '"$(some command)"'
        )

    def test_insert_expansion(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert (
            my_test_workflow().insert_expansion("[some expansion]")
            == '"$[some expansion]"'
        )

    def test_insert_expression(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        condition = "condition"
        result = my_test_workflow().insert_expression(condition)
        expected = "${{ condition }}"
        assert result == expected, f"Expected '{expected}', got {result}"

    def test_insert_github_ref(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().insert_github_ref()
        assert result == "${{ github.ref }}", (
            f"Expected '${{{{ github.ref }}}}', got {result}"
        )

    def test_insert_github_token(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().insert_github_token()
        assert result == "${{ secrets.GITHUB_TOKEN }}", (
            f"Expected '${{{{ secrets.GITHUB_TOKEN }}}}', got {result}"
        )

    def test_insert_github_workflow(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().insert_github_workflow()
        assert result == "${{ github.workflow }}", (
            f"Expected '${{{{ github.workflow }}}}', got {result}"
        )

    def test_insert_matrix_os(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().insert_matrix_os()
        assert "matrix.os" in result, "Expected 'matrix.os' in result"

    def test_insert_matrix_python_version(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().insert_matrix_python_version()
        assert "matrix.python-version" in result, (
            "Expected 'matrix.python-version' in result"
        )

    def test_insert_output_var(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert (
            my_test_workflow().insert_output_var(
                my_test_workflow().step_extract_version,
                my_test_workflow().version_var(),
            )
            == "${{ steps.extract-version.outputs.version }}"
        )

    def test_insert_output_version(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert (
            my_test_workflow().insert_output_version()
            == "${{ steps.extract-version.outputs.version }}"
        )

    def test_insert_parameter_expansion(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert (
            my_test_workflow().insert_parameter_expansion("some parameter")
            == '"${some parameter}"'
        )

    def test_insert_repo_token(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().insert_repo_token()
        assert result == "${{ secrets.REPO_TOKEN }}"

    def test_insert_version_expansion(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert my_test_workflow().insert_version_expansion() == '"${VERSION}"'

    def test_job(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().job(self.test_job, steps=[])
        assert result["job_id"] == "test-job"
        assert result["steps"] == []

        # Test with if_condition set
        result = my_test_workflow().job(
            self.test_job,
            steps=[],
            if_condition="condition",
        )
        assert result["if"] == "condition"

        # Test with job=None (line 222->224 False branch)
        result = my_test_workflow().job(
            self.test_job,
            runs_on="ubuntu-latest",
        )
        assert result["job_id"] == "test-job"

        # Test with steps=None (line 234->236 False branch)
        result = my_test_workflow().job(
            self.test_job,
            runs_on="ubuntu-latest",
            steps=None,
        )
        assert result["job_id"] == "test-job"
        assert "steps" not in result

        # Test with uses set: only runs-on must not be applied
        result = my_test_workflow().job(
            self.test_job,
            uses="$/.github/workflows/other.yml",
            runs_on="ubuntu-latest",
            strategy={"matrix": {}},
            steps=[{"name": "unused"}],
        )
        assert result["uses"] == "$/.github/workflows/other.yml"
        assert "runs-on" not in result
        assert result["strategy"] == {"matrix": {}}
        assert result["steps"] == [{"name": "unused"}]
        assert "secrets" not in result

        # Test with uses and named secrets set
        result = my_test_workflow().job(
            self.test_job,
            uses="$/.github/workflows/other.yml",
            secrets={"TOKEN": "${{ secrets.TOKEN }}"},
        )
        assert result["secrets"] == {"TOKEN": "${{ secrets.TOKEN }}"}

    def test_job_by_id(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        workflow = my_test_workflow()
        job = {"job_id": "test", "steps": []}
        assert workflow.job_by_id(lambda: job) == {"test": {"steps": []}}
        assert "job_id" not in job

    def test_job_id_from_method(self) -> None:
        """Test method."""
        result = HealthCheckWorkflowConfigFile.I.job_id_from_method(
            HealthCheckWorkflowConfigFile.I.job_health_check,
        )
        assert result == "health-check"

    def test_jobs(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        jobs = my_test_workflow().jobs()
        assert isinstance(jobs, tuple)
        assert [job()["job_id"] for job in jobs] == ["test"]

    def test_jobs_configs(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        workflow = my_test_workflow()
        assert workflow.jobs_configs() == {
            "test": {
                "name": "Test",
                "runs-on": "ubuntu-latest",
                "timeout-minutes": workflow.TIMEOUT_MINUTES_DEFAULT,
                "steps": [{"name": "Test Step", "run": "echo test"}],
            },
        }

    def test_matrix(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().matrix({"test": ["value"]})
        assert "test" in result

    def test_matrix_os(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().matrix_os()
        assert "os" in result

        result = my_test_workflow().matrix_os(os=["ubuntu-latest"])
        assert "os" in result
        assert result["os"] == ["ubuntu-latest"]

    def test_matrix_python_version(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().matrix_python_version()
        assert "python-version" in result

        result = my_test_workflow().matrix_python_version(python_versions=["3.14"])
        assert "python-version" in result
        assert result["python-version"] == ["3.14"]

    def test_name_from_id(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().name_from_id(
            "test-name-from-id",
        )
        assert result == "Test Name From Id"

    def test_on_pull_request(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().on_pull_request()
        assert "pull_request" in result, "Expected 'pull_request' in result"

        # Test with types=None (should use default types)
        result = my_test_workflow().on_pull_request(
            types=["opened", "synchronize", "reopened"],
        )
        assert result["pull_request"]["types"] == ["opened", "synchronize", "reopened"]

    def test_on_push(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().on_push()
        assert "push" in result, "Expected 'push' in result"
        assert result["push"]["branches"] == ["main"], (
            "Expected default branch to be 'main'"
        )

        result = my_test_workflow().on_push(branches=["develop", "release/*"])
        assert result["push"]["branches"] == ["develop", "release/*"]

    def test_on_schedule(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().on_schedule("0 0 * * *")
        assert "schedule" in result, "Expected 'schedule' in result"

    def test_on_workflow_call(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().on_workflow_call()
        assert result == {"workflow_call": {}}

    def test_on_workflow_call_with_secrets(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""

        class WithSecretUsage(my_test_workflow):  # type: ignore[misc]  # ty: ignore[unsupported-base]
            """Test workflow whose steps reference a secret."""

            @override
            def jobs(self) -> tuple[Callable[[], dict[str, Any]], ...]:
                """Return a job referencing `TOKEN`."""
                return (
                    lambda: {
                        "job_id": "job_a",
                        "steps": [{"env": {"TOKEN": "${{ secrets.TOKEN }}"}}],
                    },
                )

        result = WithSecretUsage().on_workflow_call()
        assert result == {"workflow_call": {"secrets": {"TOKEN": {"required": True}}}}

    def test_on_workflow_dispatch(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert my_test_workflow().on_workflow_dispatch() == {
            "workflow_dispatch": {},
        }

    def test_parent_path(
        self,
        my_test_workflow: type[WorkflowConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            result = my_test_workflow().parent_path()
            assert result == Path(".github/workflows"), (
                f"Expected '.github/workflows', got {result}"
            )

    def test_permission(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        assert workflow.permission("actions") == {"actions": "read"}
        assert workflow.permission("actions", write=True) == {"actions": "write"}

    def test_permission_comment(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert my_test_workflow().permission_comment() == "required"

    def test_permission_contents(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        assert workflow.permission_contents() == {"contents": "read"}
        assert workflow.permission_contents(write=True) == {"contents": "write"}

    def test_permission_id_token(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        assert workflow.permission_id_token() == {"id-token": "read"}
        assert workflow.permission_id_token(write=True) == {"id-token": "write"}

    def test_permission_pages(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        assert workflow.permission_pages() == {"pages": "read"}
        assert workflow.permission_pages(write=True) == {"pages": "write"}

    def test_permissions(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        assert my_test_workflow().permissions() == {}

    def test_pull_request_event_key(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert my_test_workflow().pull_request_event_key() == "pull_request"

    def test_repo_token_var(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile.I.repo_token_var() == "secrets.REPO_TOKEN"

    def test_run_name(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().run_name()
        assert result == my_test_workflow().workflow_name(), (
            "Expected run name to match workflow name"
        )

    def test_secrets_var(self) -> None:
        """Test method."""
        assert (
            HealthCheckWorkflowConfigFile.I.secrets_var("TEST_TOKEN")
            == "secrets.TEST_TOKEN"
        )

    def test_stem(self) -> None:
        """Test the explicit workflow file stems."""
        assert HealthCheckWorkflowConfigFile.I.stem() == "health-check"
        assert DeployWorkflowConfigFile.I.stem() == "deploy"
        assert ReleaseWorkflowConfigFile.I.stem() == "release"

    def test_step(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().step(
            self.test_step,
            run="echo test",
            if_condition="condition",
            uses=("action/checkout", "v2", "v2"),
            with_={"param": "value"},
            env={"ENV_VAR": "value"},
        )
        assert "name" in result
        assert "id" in result
        assert "run" in result
        assert "if" in result
        assert "uses" in result
        assert "with" in result
        assert "env" in result

    def test_step_checkout_repository(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        result = workflow.step_checkout_repository()
        assert "uses" in result, "Expected 'uses' in step"
        assert result["uses"] == f"actions/checkout@{workflow.action_checkout()[1]}"

    def test_step_download_artifact(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        result = workflow.step_download_artifact(
            self.test_step_download_artifact,
            path=Path("artifacts/download"),
        )
        assert result["id"] == "test-step-download-artifact"
        assert result["uses"] == (
            f"actions/download-artifact@{workflow.action_download_artifact()[1]}"
        )
        assert result["with"] == {"path": "artifacts/download"}

        result = workflow.step_download_artifact(
            self.test_step_download_artifact,
            path=Path("artifacts/download"),
            name="artifact",
            merge_multiple=False,
        )
        assert result["with"] == {
            "name": "artifact",
            "path": "artifacts/download",
            "merge-multiple": "false",
        }

        result = workflow.step_download_artifact(
            self.test_step_download_artifact,
            path=Path("artifacts/download"),
            pattern="artifact-*",
            merge_multiple=True,
        )
        assert result["with"] == {
            "pattern": "artifact-*",
            "path": "artifacts/download",
            "merge-multiple": "true",
        }

    def test_step_extract_version(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        step = my_test_workflow().step_extract_version()
        assert (
            step["run"]
            == 'VERSION="$(uv version --short)"\necho version="${VERSION}" >> "${GITHUB_OUTPUT}"'  # noqa: E501
        )

    def test_step_id_from_method(self) -> None:
        """Test method."""
        result = HealthCheckWorkflowConfigFile.I.step_id_from_method(
            HealthCheckWorkflowConfigFile.I.step_run_tests,
        )
        assert result == "run-tests"

    def test_step_install_dependencies(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().step_install_dependencies()
        assert "run" in result

    def test_step_setup_package_manager(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        result = workflow.step_setup_package_manager(python_version="3.14")
        assert "uses" in result, "Expected 'uses' in step"
        assert result["uses"] == f"astral-sh/setup-uv@{workflow.action_setup_uv()[1]}"
        assert result["with"]["python-version"] == "3.14"

    def test_step_update_dependencies(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().step_update_dependencies()
        assert "run" in result, f"Expected 'run' in step, got {result}"

    def test_step_upload_artifact(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        result = workflow.step_upload_artifact(
            self.test_step_upload_artifact,
            name="artifact",
            path=Path("artifacts/upload"),
        )
        assert result["id"] == "test-step-upload-artifact"
        assert result["uses"] == (
            f"actions/upload-artifact@{workflow.action_upload_artifact()[1]}"
        )
        assert result["with"] == {
            "name": "artifact",
            "path": "artifacts/upload",
            "if-no-files-found": "error",
        }

        result = workflow.step_upload_artifact(
            self.test_step_upload_artifact,
            name="artifact",
            path=Path("artifacts/upload"),
            if_no_files_found="warn",
        )
        assert result["with"]["if-no-files-found"] == "warn"

    def test_steps_core_installed_setup(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().steps_core_installed_setup()
        assert len(result) > 0

    def test_steps_core_setup(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().steps_core_setup()
        assert len(result) > 0
        assert result[1]["with"]["python-version"] == str(
            PyprojectConfigFile.I.latest_possible_python_version(level="minor"),
        )

    def test_strategy(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().strategy(strategy={})
        assert "fail-fast" in result

    def test_strategy_matrix(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        result = my_test_workflow().strategy_matrix(matrix={})
        assert "matrix" in result, "Expected 'matrix' in strategy"

    def test_strategy_matrix_os(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().strategy_matrix_os()
        assert "matrix" in result, "Expected 'matrix' in strategy"

    def test_strategy_matrix_os_and_python_version(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().strategy_matrix_os_and_python_version()
        assert "matrix" in result, "Expected 'matrix' in strategy"

    def test_used_permissions(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""

        class WithJobs(my_test_workflow):  # type: ignore[misc]  # ty: ignore[unsupported-base]
            """Test workflow with jobs requesting overlapping permissions."""

            @override
            def jobs(self) -> tuple[Callable[[], dict[str, Any]], ...]:
                """Return jobs with overlapping and write-escalating permissions."""
                return (
                    lambda: {
                        "job_id": "job_a",
                        "permissions": {"pages": "write", "contents": "read"},
                    },
                    lambda: {
                        "job_id": "job_b",
                        "permissions": {"contents": "read"},
                    },
                    lambda: {"job_id": "job_c"},
                )

        result = WithJobs().used_permissions()
        assert result == {"contents": "read", "pages": "write"}
        assert list(result.keys()) == ["contents", "pages"]

    def test_used_secrets(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        assert my_test_workflow().used_secrets() == []

    def test_used_secrets_discovered(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""

        class WithSecretUsage(my_test_workflow):  # type: ignore[misc]  # ty: ignore[unsupported-base]
            """Test workflow whose steps reference secrets."""

            @override
            def jobs(self) -> tuple[Callable[[], dict[str, Any]], ...]:
                """Return a job with secrets, GITHUB_TOKEN, and a non-string leaf."""
                return (
                    lambda: {
                        "job_id": "job_a",
                        "continue-on-error": True,
                        "steps": [
                            {"env": {"TOKEN": "${{ secrets.TOKEN }}"}},
                            {"with": {"gh-token": "${{ secrets.GITHUB_TOKEN }}"}},
                        ],
                    },
                    lambda: {
                        "job_id": "job_b",
                        "if": "${{ secrets.TOKEN != '' }}",
                    },
                )

        result = WithSecretUsage().used_secrets()
        assert result == ["TOKEN"]

    def test_used_secrets_mapping(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().used_secrets_mapping()
        assert result == {}

        class WithSecretUsage(my_test_workflow):  # type: ignore[misc]  # ty: ignore[unsupported-base]
            """Test workflow whose steps reference a secret."""

            @override
            def jobs(self) -> tuple[Callable[[], dict[str, Any]], ...]:
                """Return a job referencing `TOKEN`."""
                return (
                    lambda: {
                        "job_id": "job_a",
                        "steps": [{"env": {"TOKEN": "${{ secrets.TOKEN }}"}}],
                    },
                )

        result = WithSecretUsage().used_secrets_mapping()
        assert result == {"TOKEN": "${{ secrets.TOKEN }}"}

    def test_uses(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        assert (
            my_test_workflow().uses("action-name", "some-ref") == "action-name@some-ref"
        )

    def test_version_var(self, my_test_workflow: type[WorkflowConfigFile]) -> None:
        """Test method."""
        assert my_test_workflow().version_var() == "VERSION"

    def test_workflow_call_reference(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        workflow = my_test_workflow()
        result = workflow.workflow_call_reference()
        assert result == f"$/{workflow.path().as_posix()}"

    def test_workflow_name(self) -> None:
        """Test method."""
        assert HealthCheckWorkflowConfigFile().workflow_name() == "Health Check"
        assert DeployWorkflowConfigFile().workflow_name() == "Deploy"

    def test_workflow_triggers(
        self,
        my_test_workflow: type[WorkflowConfigFile],
    ) -> None:
        """Test method."""
        result = my_test_workflow().workflow_triggers()
        assert "workflow_dispatch" in result, "Expected 'workflow_dispatch' in triggers"


@pytest.fixture
def my_test_workflow(
    config_file_factory: Callable[[type[WorkflowConfigFile]], type[WorkflowConfigFile]],
) -> type[WorkflowConfigFile]:
    """Create a test workflow class with tmp_path."""

    class MyTestWorkflowConfigFileClass(config_file_factory(WorkflowConfigFile)):  # ty: ignore[unsupported-base]
        """Test workflow class with tmp_path override."""

        @override
        def stem(self) -> str:
            """Get the stem."""
            return "test_workflow"

        @override
        def workflow_triggers(self) -> dict[str, Any]:
            """Get the workflow triggers."""
            return {"workflow_dispatch": {}}

        @override
        def jobs(self) -> tuple[Callable[[], dict[str, Any]], ...]:
            """Get the workflow jobs."""
            return (self.job_test,)

        def job_test(self) -> dict[str, Any]:
            """Build the test job."""
            return self.job(
                self.job_test,
                steps=[{"name": "Test Step", "run": "echo test"}],
            )

    return MyTestWorkflowConfigFileClass
