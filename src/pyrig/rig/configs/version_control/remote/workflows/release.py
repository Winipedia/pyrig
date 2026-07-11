"""Workflow configuration for automated GitHub release creation."""

from typing import Any

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.version_control.remote.settings import (
    RepoSettingsConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.version_control.controller import VersionController


class ReleaseWorkflowConfigFile(WorkflowConfigFile):
    """Generator for the `release.yml` GitHub Actions workflow.

    The workflow is triggered by completion of the health check workflow on
    the default branch, but its job only proceeds when that health check run
    both succeeded and was itself triggered by a push — so the daily
    scheduled run, manual dispatches of the health check, and pull request
    runs never produce a release. A qualifying run tags the current version,
    applies repository settings and branch protection rulesets, generates a
    changelog, and publishes a GitHub release.
    """

    def stem(self) -> str:
        """Return `"release"`, giving the path `.github/workflows/release.yml`."""
        return "release"

    def workflow_triggers(self) -> dict[str, Any]:
        """Return the triggers for the release workflow.

        A single `workflow_run` trigger that fires when the health check
        workflow completes on the default branch.

        Returns:
            Trigger configuration dict with a `workflow_run` entry.
        """
        return self.on_workflow_run(
            workflows=[HealthCheckWorkflowConfigFile.I.workflow_name()],
            branches=[VersionController.I.default_branch()],
        )

    def job(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Build a job gated on the workflow having been triggered by a push.

        Every job built through this method only runs when the run that
        triggered this workflow both succeeded and was itself triggered by
        a push.

        Args:
            *args: Positional arguments forwarded to the base implementation.
            **kwargs: Keyword arguments forwarded to the base implementation.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        return super().job(
            *args,
            if_condition=self.if_workflow_run_is_success_and_push_triggered(),
            **kwargs,
        )

    def jobs(self) -> dict[str, Any]:
        """Return all jobs for the release workflow.

        Returns:
            Dict containing the single release job.
        """
        return {**self.job_publish()}

    def job_publish(self) -> dict[str, Any]:
        """Return the job that tags, configures, and releases the project.

        Requests `contents: write` permission at the job level, which is
        required to push the version tag and create the GitHub release.

        Returns:
            Job configuration dict keyed by the job name, containing the
            guard condition and the ordered release steps.
        """
        return self.job(
            self.job_publish,
            permissions={"contents": "write"},
            steps=self.steps_publish(),
        )

    def steps_publish(self) -> list[dict[str, Any]]:
        """Return the ordered steps for the release job.

        Returns:
            Steps that perform the full release sequence: environment setup,
            applying repository settings and rulesets, creating and pushing
            the version tag, exporting the version, generating a changelog,
            and publishing the GitHub release.
        """
        return [
            *self.steps_core_setup(),
            *self.steps_configure_repository(),
            self.step_create_tag(),
            self.step_push_tag(),
            self.step_extract_version(),
            self.step_build_changelog(),
            self.step_create_release(),
        ]

    def steps_configure_repository(self) -> list[dict[str, Any]]:
        """Return the ordered steps that apply repository settings and rulesets.

        Returns:
            Two steps in sequence: apply general repository settings, then
            upsert all rulesets.
        """
        return [
            self.step_apply_repository_settings(),
            self.step_apply_rulesets(),
        ]

    def step_apply_repository_settings(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that patches general repository settings via the GitHub API.

        Reads the `repository` key from the settings file and sends it as a
        `PATCH /repos/{owner}/{repo}` request using `gh api`.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that pipes the repository settings dict into `gh api`.
        """
        repo = self.insert_repository()
        key = RepoSettingsConfigFile.I.repository_key()
        path = RepoSettingsConfigFile.I.path().as_posix()
        run = f"jq '.{key}' {path} | gh api --method PATCH \"repos/{repo}\" --input -"
        return self.step(
            self.step_apply_repository_settings,
            run=run,
            env={"GH_TOKEN": self.insert_repo_token()},
            step=step,
        )

    def step_apply_rulesets(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that upserts all rulesets from the settings file.

        For each ruleset in the `rulesets` array, looks up whether a ruleset
        with that name already exists. Sends the full ruleset configuration
        with `gh api`, using `POST` to create it if no matching ruleset was
        found or `PUT` to update it in place otherwise.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step containing the shell loop that upserts each ruleset.
        """
        repo = self.insert_repository()
        key = RepoSettingsConfigFile.I.rulesets_key()
        path = RepoSettingsConfigFile.I.path().as_posix()
        run = f"""\
REPO="{repo}"
jq -c '.{key}[]' {path} | while read ruleset; do
  ID=$(gh api "repos/$REPO/rulesets" |
    jq -r --argjson r "$ruleset" '.[] | select(.name==$r.name) | .id')
  if [ -z "$ID" ]; then METHOD="POST"; else METHOD="PUT"; fi
  gh api --method "$METHOD" "repos/$REPO/rulesets${{ID:+/$ID}}" --input - <<< "$ruleset"
done"""
        return self.step(
            self.step_apply_rulesets,
            run=run,
            env={"GH_TOKEN": self.insert_repo_token()},
            step=step,
        )

    def step_create_tag(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that creates a version tag.

        The tag name (e.g. `1.2.3`) is resolved from the project version at
        runtime, when the step executes.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs `git tag` to create the version tag.
        """
        return self.step(
            self.step_create_tag,
            run=str(VersionController.I.tag_args(tag=self.shell_insert_version())),
            step=step,
        )

    def step_push_tag(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that pushes the version tag to the remote repository.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs `git push origin <tag>`.
        """
        return self.step(
            self.step_push_tag,
            run=str(
                VersionController.I.push_origin_tag_args(
                    tag=self.shell_insert_version(),
                ),
            ),
            step=step,
        )

    def step_extract_version(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that writes the current version to `GITHUB_OUTPUT`.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that appends `version=<x.y.z>` to the `$GITHUB_OUTPUT` file.
        """
        return self.step(
            self.step_extract_version,
            run=f'echo "version={self.shell_insert_version()}" >> $GITHUB_OUTPUT',
            step=step,
        )

    def step_build_changelog(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that generates a changelog from commit history.

        Uses `mikepenz/release-changelog-builder-action` to generate release
        notes from commits since the previous tag.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using `mikepenz/release-changelog-builder-action@develop`.
        """
        return self.step(
            self.step_build_changelog,
            uses="mikepenz/release-changelog-builder-action@develop",
            with_={"token": self.insert_github_token()},
            step=step,
        )

    def step_create_release(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that creates a GitHub release.

        Uses `ncipollo/release-action` to create a release tagged with the
        extracted version and the generated changelog as its body.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using `ncipollo/release-action@main`.
        """
        version = self.insert_version_from_extract_version_step()
        return self.step(
            self.step_create_release,
            uses="ncipollo/release-action@main",
            with_={
                "tag": version,
                "name": version,
                "body": self.insert_changelog(),
            },
            step=step,
        )

    def insert_version_from_extract_version_step(self) -> str:
        """Return the expression that resolves to the extracted version output.

        Returns:
            GitHub Actions expression for `steps.extract-version.outputs.version`.
        """
        return self.insert_expression(
            f"steps.{self.id_from_method(self.step_extract_version)}.outputs.version",
        )

    def insert_changelog(self) -> str:
        """Return the expression that resolves to the generated changelog output.

        Returns:
            GitHub Actions expression for `steps.build-changelog.outputs.changelog`.
        """
        return self.insert_expression(
            f"steps.{self.id_from_method(self.step_build_changelog)}.outputs.changelog",
        )
