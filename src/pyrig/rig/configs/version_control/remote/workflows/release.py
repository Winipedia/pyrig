"""Workflow configuration for automated GitHub release creation."""

from typing import Any

from pyrig.rig.configs.base.workflow import WorkflowConfigFile
from pyrig.rig.configs.version_control.remote.settings import (
    RepoSettingsConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.version_control.version_controller import VersionController


class ReleaseWorkflowConfigFile(WorkflowConfigFile):
    """Generates the ``release.yml`` GitHub Actions workflow.

    This workflow is triggered when the health check workflow completes on the
    default branch. The release job only runs when the triggering run succeeded
    and was not a scheduled (cron) run, so the daily health check run does not
    create a release every day. It creates and pushes a version tag, generates
    a changelog from commit history, and publishes a GitHub release.

    Release process (in order):
        1. Check out the repository (authenticated with the automatic
           ``GITHUB_TOKEN``) and install the uv package manager.
        2. Apply general repository settings and upsert rulesets from
           ``.github/settings.json``.
        3. Create a version tag (e.g. ``1.2.3``) and push it to the remote.
        4. Export the version string to ``GITHUB_OUTPUT``.
        5. Generate a changelog from commits since the last tag.
        6. Publish the GitHub release with the changelog body.

    Permissions required:
        - ``contents: write`` — push the version tag and create the release.
    """

    def stem(self) -> str:
        """Return the workflow filename stem.

        Returns:
            ``"release"``, which produces ``release.yml`` as the output file.
        """
        return "release"

    def workflow_triggers(self) -> dict[str, Any]:
        """Build the workflow trigger configuration.

        Extends the default ``workflow_dispatch`` trigger (inherited from the
        base class) with a ``workflow_run`` trigger that fires when
        :class:`~pyrig.rig.configs.remote_version_control.workflows.health_check.HealthCheckWorkflowConfigFile`
        completes on the default branch.

        Returns:
            Trigger configuration containing both ``workflow_dispatch`` and
            ``workflow_run`` triggers.
        """
        triggers = super().workflow_triggers()
        triggers.update(
            self.on_workflow_run(
                workflows=[HealthCheckWorkflowConfigFile.I.workflow_name()],
                branches=[VersionController.I.default_branch()],
            )
        )
        return triggers

    def job(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Build a job gated on a successful, non-scheduled triggering run.

        Overrides :meth:`WorkflowConfigFile.job` to inject an ``if`` condition
        (via :meth:`if_workflow_run_is_success_and_not_cron_triggered`) into
        every job in this workflow, so jobs run only when the triggering
        ``workflow_run`` succeeded and was not a scheduled (cron) run.

        Args:
            *args: Positional arguments forwarded to
                :meth:`WorkflowConfigFile.job`.
            **kwargs: Keyword arguments forwarded to
                :meth:`WorkflowConfigFile.job`.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        return super().job(
            *args,
            if_condition=self.if_workflow_run_is_success_and_not_cron_triggered(),
            **kwargs,
        )

    def jobs(self) -> dict[str, Any]:
        """Build the complete jobs configuration for the workflow.

        Returns:
            Dict containing the single release job.
        """
        return {**self.job_publish()}

    def job_publish(self) -> dict[str, Any]:
        """Build the release job configuration.

        The job runs only when both of these conditions hold:
            - The triggering health check workflow run completed successfully.
            - The triggering run was not a scheduled (cron) run.

        The cron guard prevents the daily scheduled health check run from
        creating a release every day.

        Requests ``contents: write`` permission at the job level, which is
        required to push the version tag and create the GitHub release.

        Returns:
            Job configuration dict keyed by the job name, containing the
            guard condition and the ordered release steps.
        """
        return self.job(
            job_func=self.job_publish,
            permissions={"contents": "write"},
            steps=self.steps_publish(),
        )

    def steps_publish(self) -> list[dict[str, Any]]:
        """Build the ordered list of steps for the release job.

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
        """Build the ordered steps that apply repository settings and branch protection.

        Returns:
            Two steps in sequence: apply general repository settings, then
            upsert all rulesets from ``.github/settings.json``.
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

        Reads the ``repository`` key from ``.github/settings.json`` and sends it
        as a ``PATCH /repos/{owner}/{repo}`` request using ``gh api``.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that pipes the repository settings dict into ``gh api``.
        """
        repo = self.insert_repository()
        key = RepoSettingsConfigFile.I.repository_key()
        path = RepoSettingsConfigFile.I.path().as_posix()
        run = f"jq '.{key}' {path} | gh api --method PATCH \"repos/{repo}\" --input -"
        return self.step(
            step_func=self.step_apply_repository_settings,
            run=run,
            env={"GH_TOKEN": self.insert_repo_token()},
            step=step,
        )

    def step_apply_rulesets(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that upserts all rulesets from ``.github/settings.json``.

        For each ruleset in the ``rulesets`` array, looks up whether a ruleset
        with that name already exists. If not, POSTs a minimal disabled placeholder
        to obtain an ID. Then PUTs the full configuration to that ID. This
        check-then-create-then-apply pattern avoids 409 conflicts and requires no
        ``$GITHUB_ENV`` handoff between steps.

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
            step_func=self.step_apply_rulesets,
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

        Creates a tag named ``<version>`` (e.g. ``1.2.3``).  The version
        string is resolved at runtime via :meth:`shell_insert_version`.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``git tag`` to create the version tag.
        """
        return self.step(
            step_func=self.step_create_tag,
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
            Step that runs ``git push origin <tag>``.
        """
        return self.step(
            step_func=self.step_push_tag,
            run=str(
                VersionController.I.push_origin_tag_args(
                    tag=self.shell_insert_version()
                )
            ),
            step=step,
        )

    def step_extract_version(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that writes the current version to ``GITHUB_OUTPUT``.

        Evaluates :meth:`shell_insert_version` (``$(uv version --short)``) at
        runtime and appends ``version=<x.y.z>`` to the ``$GITHUB_OUTPUT``
        file.  Downstream steps can reference the value via
        :meth:`insert_version_from_extract_version_step`.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that exports the version as a GitHub Actions output.
        """
        return self.step(
            step_func=self.step_extract_version,
            run=f'echo "version={self.shell_insert_version()}" >> $GITHUB_OUTPUT',
            step=step,
        )

    def step_build_changelog(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that generates a changelog from commit history.

        Uses ``mikepenz/release-changelog-builder-action`` to generate release
        notes from commits since the previous tag.  The output is available
        via :meth:`insert_changelog` in subsequent steps.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using ``mikepenz/release-changelog-builder-action@develop``.
        """
        return self.step(
            step_func=self.step_build_changelog,
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

        Uses ``ncipollo/release-action`` to create a release tagged with the
        version extracted by :meth:`step_extract_version`.  Uses the changelog
        generated by :meth:`step_build_changelog` as the release body.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using ``ncipollo/release-action@main``.
        """
        version = self.insert_version_from_extract_version_step()
        return self.step(
            step_func=self.step_create_release,
            uses="ncipollo/release-action@main",
            with_={
                "tag": version,
                "name": version,
                "body": self.insert_changelog(),
            },
            step=step,
        )

    def insert_version_from_extract_version_step(self) -> str:
        """Get the expression that reads the version from the extract step output.

        References the ``version`` output produced by
        :meth:`step_extract_version` so that subsequent steps can consume the
        resolved version string.

        Returns:
            GitHub Actions expression for
            ``steps.extract-version.outputs.version``.
        """
        # make dynamic with self.make_id_from_func(self.step_extract_version)
        return self.insert_expression(
            f"steps.{self.make_id_from_func(self.step_extract_version)}.outputs.version"
        )

    def insert_changelog(self) -> str:
        """Get the expression that reads the changelog from the build step output.

        References the ``changelog`` output produced by
        :meth:`step_build_changelog`.

        Returns:
            GitHub Actions expression for
            ``steps.build-changelog.outputs.changelog``.
        """
        return self.insert_expression(
            f"steps.{self.make_id_from_func(self.step_build_changelog)}.outputs.changelog"
        )
