"""Tests for the documentation workflow."""

from pyrig.core.resources import resource_content
from pyrig.core.strings import read_text_utf8
from pyrig.rig import resources
from pyrig.rig.configs.version_control.remote.workflows.documentation import (
    DocumentationWorkflowConfigFile,
)


class TestDocumentationWorkflowConfigFile:
    """Tests for the reusable documentation workflow."""

    def test_action_configure_pages(self) -> None:
        """Check the configured Pages action and its persisted reference."""
        workflow = DocumentationWorkflowConfigFile.I
        action, ref, tag = workflow.action_configure_pages()
        assert (action, ref, tag) == tuple(
            resource_content("ACTION_CONFIGURE_PAGES", resources).splitlines(),
        )
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(workflow.path())

    def test_action_deploy_pages(self) -> None:
        """Check the deploy action and its persisted reference."""
        workflow = DocumentationWorkflowConfigFile.I
        action, ref, tag = workflow.action_deploy_pages()
        assert (action, ref, tag) == tuple(
            resource_content("ACTION_DEPLOY_PAGES", resources).splitlines(),
        )
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(workflow.path())

    def test_action_upload_pages_artifact(self) -> None:
        """Check the Pages artifact action and its persisted reference."""
        workflow = DocumentationWorkflowConfigFile.I
        action, ref, tag = workflow.action_upload_pages_artifact()
        assert (action, ref, tag) == tuple(
            resource_content("ACTION_UPLOAD_PAGES_ARTIFACT", resources).splitlines(),
        )
        assert f'"uses": "{action}@{ref}"  # {tag}' in read_text_utf8(workflow.path())

    def test_concurrency_cancel_in_progress(self) -> None:
        """Check a deployment cannot be cancelled by a subsequent call."""
        workflow = DocumentationWorkflowConfigFile.I
        assert workflow.concurrency_cancel_in_progress() is False

    def test_job_build(self) -> None:
        """Check the build job configuration."""
        workflow = DocumentationWorkflowConfigFile.I
        job = workflow.job_build()
        timeout = 60
        assert job["job_id"] == "build"
        assert job["permissions"] == {"contents": "read"}
        assert job["timeout-minutes"] == timeout
        assert job["steps"] == workflow.steps_build()
        assert "environment" not in job
        assert "needs" not in job
        assert "secrets.REPO_TOKEN" not in str(job)

    def test_job_build_permissions(self) -> None:
        """Check the build only needs checkout permission."""
        assert DocumentationWorkflowConfigFile.I.job_build_permissions() == {
            "contents": "read",
        }

    def test_job_deploy(self) -> None:
        """Check deployment runs after building and uses the Pages environment."""
        workflow = DocumentationWorkflowConfigFile.I
        job = workflow.job_deploy()
        timeout = 30
        assert job["job_id"] == "deploy"
        assert job["environment"] == "documentation"
        assert job["needs"] == ["build"]
        assert job["permissions"] == {"id-token": "write", "pages": "write"}
        assert job["timeout-minutes"] == timeout
        assert job["steps"] == workflow.steps_deploy()

    def test_job_deploy_needs(self) -> None:
        """Check deployment depends on the build."""
        workflow = DocumentationWorkflowConfigFile.I
        assert workflow.job_deploy_needs() == (workflow.job_build,)

    def test_job_deploy_permissions(self) -> None:
        """Check the Pages deployment permissions."""
        assert DocumentationWorkflowConfigFile.I.job_deploy_permissions() == {
            "id-token": "write",
            "pages": "write",
        }

    def test_jobs(self) -> None:
        """Check both documentation jobs are present."""
        workflow = DocumentationWorkflowConfigFile.I
        assert workflow.jobs() == (workflow.job_build, workflow.job_deploy)

    def test_stem(self) -> None:
        """Check the workflow filename."""
        assert DocumentationWorkflowConfigFile.I.stem() == "documentation"

    def test_step_build_documentation(self) -> None:
        """Check the documentation build command."""
        assert DocumentationWorkflowConfigFile.I.step_build_documentation()["run"]

    def test_step_configure_pages(self) -> None:
        """Check Pages enablement uses the repository token."""
        workflow = DocumentationWorkflowConfigFile.I
        step = workflow.step_configure_pages()
        assert step["uses"] == (
            f"actions/configure-pages@{workflow.action_configure_pages()[1]}"
        )
        assert step["with"] == {
            "enablement": "true",
            "token": workflow.insert_repo_token(),
        }

    def test_step_deploy_documentation(self) -> None:
        """Check the Pages deploy action."""
        workflow = DocumentationWorkflowConfigFile.I
        assert workflow.step_deploy_documentation()["uses"] == (
            f"actions/deploy-pages@{workflow.action_deploy_pages()[1]}"
        )

    def test_step_upload_documentation(self) -> None:
        """Check the Pages artifact upload action and site path."""
        workflow = DocumentationWorkflowConfigFile.I
        step = workflow.step_upload_documentation()
        assert step["uses"] == (
            "actions/upload-pages-artifact@"
            f"{workflow.action_upload_pages_artifact()[1]}"
        )
        assert step["with"]["path"] == "site"

    def test_steps_build(self) -> None:
        """Check build and upload run after setup."""
        workflow = DocumentationWorkflowConfigFile.I
        assert workflow.steps_build() == [
            *workflow.steps_core_installed_setup(),
            workflow.step_build_documentation(),
            workflow.step_upload_documentation(),
        ]

    def test_steps_deploy(self) -> None:
        """Check Pages enablement precedes deployment."""
        workflow = DocumentationWorkflowConfigFile.I
        assert workflow.steps_deploy() == [
            workflow.step_configure_pages(),
            workflow.step_deploy_documentation(),
        ]

    def test_used_permissions(self) -> None:
        """Check permissions are aggregated for the caller."""
        assert DocumentationWorkflowConfigFile.I.used_permissions() == {
            "contents": "read",
            "id-token": "write",
            "pages": "write",
        }

    def test_used_secrets(self) -> None:
        """Check the repository token is detected."""
        assert DocumentationWorkflowConfigFile.I.used_secrets() == ["REPO_TOKEN"]

    def test_workflow_triggers(self) -> None:
        """Check the secret is declared for reusable calls."""
        assert DocumentationWorkflowConfigFile.I.workflow_triggers() == {
            "workflow_call": {"secrets": {"REPO_TOKEN": {"required": True}}},
        }
