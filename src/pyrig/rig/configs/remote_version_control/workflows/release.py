"""Workflow configuration for automated GitHub release creation."""

from typing import Any

from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.remote_version_control.workflows.build import (
    BuildWorkflowConfigFile,
)


class ReleaseWorkflowConfigFile(WorkflowConfigFile):
    """Generates the ``release.yml`` GitHub Actions workflow.

    This workflow is triggered when the build workflow completes. The release
    job only runs when the triggering run succeeded. It creates and pushes a
    version tag, downloads build artifacts from the triggering run, generates
    a changelog from commit history, and publishes a GitHub release with the
    artifacts attached.

    Release process (in order):
        1. Check out the repository using ``REPO_TOKEN`` and configure git
           credentials.
        2. Install dependencies.
        3. Create a version tag (e.g. ``v1.2.3``) and push it to the remote.
        4. Export the version string to ``GITHUB_OUTPUT``.
        5. Download build artifacts from the triggering workflow run into
           ``dist/``.
        6. Generate a changelog from commits since the last tag.
        7. Publish the GitHub release with artifacts and the changelog body.

    Permissions required:
        - ``contents: write`` — push commits, tags, and create releases.
        - ``actions: read`` — download artifacts from the triggering run.

    Example:
        >>> from pyrig.rig.configs.remote_version_control.workflows.release import (
        ...     ReleaseWorkflowConfigFile,
        ... )
        >>> ReleaseWorkflowConfigFile.I.validate()
    """

    def stem(self) -> str:
        """Return the workflow filename stem.

        Returns:
            ``"release"``, which produces ``release.yml`` as the output file.
        """
        return "release"

    def workflow_triggers(self) -> ConfigDict:
        """Build the workflow trigger configuration.

        Extends the default ``workflow_dispatch`` trigger (inherited from the
        base class) with a ``workflow_run`` trigger that fires when
        :class:`~pyrig.rig.configs.remote_version_control.workflows.build.BuildWorkflowConfigFile`
        completes.

        Returns:
            Trigger configuration containing both ``workflow_dispatch`` and
            ``workflow_run`` triggers.
        """
        triggers = super().workflow_triggers()
        triggers.update(
            self.on_workflow_run(
                workflows=[BuildWorkflowConfigFile.I.workflow_name()],
            )
        )
        return triggers

    def permissions(self) -> ConfigDict:
        """Build the workflow permission configuration.

        Grants ``contents: write`` to allow pushing commits, creating version
        tags, and publishing GitHub releases. Grants ``actions: read`` to
        allow downloading artifacts from the triggering build workflow run.

        Returns:
            Permission map with ``contents`` set to ``"write"`` and
            ``actions`` set to ``"read"``.
        """
        permissions = super().permissions()
        permissions["contents"] = "write"
        permissions["actions"] = "read"
        return permissions

    def jobs(self) -> ConfigDict:
        """Build the complete jobs configuration for the workflow.

        Returns:
            Dict containing the single release job.
        """
        jobs: ConfigDict = {}
        jobs.update(self.job_distributions())
        return jobs

    def job_distributions(self) -> ConfigDict:
        """Build the release job configuration.

        The job is guarded by
        :meth:`~WorkflowConfigFile.if_workflow_run_is_success`, so it only
        runs when the triggering workflow run concluded successfully.

        Returns:
            Job configuration dict keyed by the job name, containing the
            success condition and the ordered release steps.
        """
        return self.job(
            job_func=self.job_distributions,
            if_condition=self.if_workflow_run_is_success(),
            steps=self.steps_distributions(),
        )

    def steps_distributions(self) -> list[dict[str, Any]]:
        """Build the ordered list of steps for the release job.

        Returns:
            Steps that perform the full release sequence: environment setup
            and dependency installation, creating and pushing the version
            tag, exporting the version, downloading build artifacts,
            generating a changelog, and publishing the GitHub release.
        """
        return [
            *self.steps_core_installed_setup(repo_token=True),
            self.step_create_tag(),
            self.step_push_tag(),
            self.step_extract_version(),
            self.step_download_artifacts_from_workflow_run(),
            self.step_build_changelog(),
            self.step_create_release(),
        ]
