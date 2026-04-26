"""GitHub Actions workflow YAML generation utilities and abstract base classes."""

from abc import abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pyrig.core.introspection.packages import src_package_is_pyrig
from pyrig.core.strings import (
    make_name_from_obj,
    read_text_utf8,
    split_on_uppercase,
)
from pyrig.rig.builders.base.builder import BuilderConfigFile
from pyrig.rig.cli.subcommands import build, protect_repo
from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.yml import DictYmlConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.container_engine import (
    ContainerEngine,
)
from pyrig.rig.tools.dependency_auditor import DependencyAuditor
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.package_index import PackageIndex
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pre_committer import PreCommitter
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.tools.project_coverage_tester import ProjectCoverageTester
from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.remote_version_controller import RemoteVersionController
from pyrig.rig.tools.version_controller import VersionController


class WorkflowConfigFile(DictYmlConfigFile):
    """Abstract base class for generating GitHub Actions workflow YAML files.

    Subclasses define specific workflows by implementing :meth:`jobs` and
    optionally overriding the trigger, permission, and environment methods.
    The base class provides a rich set of composable building blocks for steps,
    jobs, strategies, triggers, and expression helpers so subclasses can
    assemble complete workflows without writing raw YAML.

    Subclasses should:
        1. Implement :meth:`jobs` to define the workflow jobs.
        2. Override :meth:`workflow_triggers` to control when the workflow runs.
        3. Override :meth:`permissions` if the workflow needs elevated access.

    Attributes:
        UBUNTU_LATEST (str): Runner label for Ubuntu (``"ubuntu-latest"``)
        WINDOWS_LATEST (str): Runner label for Windows (``"windows-latest"``)
        MACOS_LATEST (str): Runner label for macOS (``"macos-latest"``)

    Example:
        >>> from pyrig.rig.configs.base.workflow import WorkflowConfigFile
        >>>
        >>> class MyWorkflowConfigFile(WorkflowConfigFile):
        ...
        ...     def jobs(self) -> ConfigDict:
        ...         return self.job(
        ...             job_func=self.jobs,
        ...             steps=[
        ...                 *self.steps_core_installed_setup(),
        ...                 self.step_run_tests(),
        ...             ],
        ...         )
        ...
        ...
        ...     def workflow_triggers(self) -> ConfigDict:
        ...         triggers = super().workflow_triggers()
        ...         triggers.update(self.on_push())
        ...         return triggers
    """

    UBUNTU_LATEST = "ubuntu-latest"
    WINDOWS_LATEST = "windows-latest"
    MACOS_LATEST = "macos-latest"

    def _configs(self) -> ConfigDict:
        """Assemble the complete workflow configuration dict.

        Returns:
            Top-level workflow configuration with ``name``, ``on``,
            ``permissions``, ``run-name``, ``defaults``, ``env``, and ``jobs``
            keys populated from the overridable methods.
        """
        return {
            "name": self.workflow_name(),
            "on": self.workflow_triggers(),
            "permissions": self.permissions(),
            "run-name": self.run_name(),
            "defaults": self.defaults(),
            "env": self.global_env(),
            "jobs": self.jobs(),
        }

    def parent_path(self) -> Path:
        """Get the parent directory for workflow files.

        Returns:
            Path to .github/workflows directory.
        """
        return Path(".github/workflows")

    def is_correct(self) -> bool:
        """Check whether the workflow configuration is correct.

        Extends the base correctness check with special handling for
        intentionally empty workflow files.  When a workflow file is found to
        be empty, a valid YAML configuration is written with all job steps
        replaced by an opt-out echo step — this keeps the file parseable by
        GitHub Actions while effectively disabling the workflow.

        A workflow is also considered correct when every job already contains
        only the opt-out step (i.e. the workflow was previously disabled).

        Returns:
            ``True`` if the configuration matches the expected content, or if
            the workflow has been intentionally opted out.
        """
        correct = super().is_correct()

        if read_text_utf8(self.path()) == "":
            config = self.configs()
            jobs = config["jobs"]
            for job in jobs.values():
                job["steps"] = [self.step_opt_out_of_workflow()]
            self.dump(config)

        config = self.load()
        jobs = config["jobs"]
        opted_out = all(
            job["steps"] == [self.step_opt_out_of_workflow()] for job in jobs.values()
        )

        return correct or opted_out

    # Overridable WorkflowConfigFile Parts
    # ----------------------------------------------------------------------------
    @abstractmethod
    def jobs(self) -> ConfigDict:
        """Get the workflow jobs.

        Subclasses must implement this to define their jobs.

        Returns:
            Dict mapping job IDs to job configurations.
        """

    def workflow_triggers(self) -> ConfigDict:
        """Get the workflow triggers.

        Override to customize when the workflow runs.
        Default is manual workflow_dispatch only.

        Returns:
            Dict of trigger configurations.
        """
        return self.on_workflow_dispatch()

    def permissions(self) -> ConfigDict:
        """Get the workflow permissions.

        Override to request additional permissions.
        Default is no extra permissions.

        Returns:
            Dict of permission settings.
        """
        return {}

    def defaults(self) -> ConfigDict:
        """Get the workflow defaults.

        Override to customize default settings.
        Default uses bash shell.

        Returns:
            Dict of default settings.
        """
        return {"run": {"shell": "bash"}}

    def global_env(self) -> ConfigDict:
        """Get global environment variables applied to all workflow jobs.

        Override to add custom variables.  By default sets two variables:
        one to prevent Python from writing ``.pyc`` bytecode files, and
        one to prevent uv from automatically syncing the environment on
        every invocation.

        Returns:
            Dict of environment variable names to their values.
        """
        return {
            ProgrammingLanguage.I.no_bytecode_env_var(): 1,
            PackageManager.I.no_auto_install_env_var(): 1,
        }

    # WorkflowConfigFile Conventions
    # ----------------------------------------------------------------------------
    def workflow_name(self) -> str:
        """Derive a human-readable name from the class name.

        Removes the ``WorkflowConfigFile`` suffix and splits the remainder on
        uppercase letters to produce a space-separated title.

        Returns:
            Workflow name, e.g. ``"Health Check"`` for
            ``HealthCheckWorkflowConfigFile``.
        """
        name = self.__class__.__name__.removesuffix(WorkflowConfigFile.__name__)
        return " ".join(split_on_uppercase(name))

    def run_name(self) -> str:
        """Get the display name shown for individual workflow runs.

        Returns:
            The workflow name by default.
        """
        return self.workflow_name()

    # Build Utilities
    # ----------------------------------------------------------------------------
    def job(  # noqa: PLR0913
        self,
        job_func: Callable[..., Any],
        needs: list[str] | None = None,
        strategy: dict[str, Any] | None = None,
        permissions: dict[str, Any] | None = None,
        runs_on: str = UBUNTU_LATEST,
        if_condition: str | None = None,
        steps: list[dict[str, Any]] | None = None,
        job: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a job configuration dict.

        Args:
            job_func: Function representing this job; its name is used to derive
                the job ID.
            needs: IDs of jobs that must complete before this job starts.
            strategy: Matrix or other strategy configuration.
            permissions: Job-level permissions override.
            runs_on: Runner label.  Defaults to ``ubuntu-latest``.
            if_condition: GitHub Actions conditional expression controlling
                whether the job runs.
            steps: Ordered list of step configurations.
            job: Additional job-level keys to merge into the configuration.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        name = self.make_id_from_func(job_func)
        if job is None:
            job = {}
        job_config: dict[str, Any] = {}
        if needs is not None:
            job_config["needs"] = needs
        if strategy is not None:
            job_config["strategy"] = strategy
        if permissions is not None:
            job_config["permissions"] = permissions
        job_config["runs-on"] = runs_on
        if if_condition is not None:
            job_config["if"] = if_condition
        if steps is not None:
            job_config["steps"] = steps
        job_config.update(job)
        return {name: job_config}

    def step(  # noqa: PLR0913
        self,
        step_func: Callable[..., Any],
        run: str | None = None,
        if_condition: str | None = None,
        uses: str | None = None,
        with_: dict[str, Any] | None = None,
        env: dict[str, Any] | None = None,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step configuration dict.

        Args:
            step_func: Function representing this step; its name is used to
                derive the step ``name`` and ``id`` fields.
            run: Shell command to execute.
            if_condition: GitHub Actions conditional expression controlling
                whether the step runs.
            uses: GitHub Action reference to use (e.g.
                ``"actions/checkout@main"``).
            with_: Input parameters passed to the action.
            env: Step-level environment variables.
            step: Additional keys to merge into the step configuration.

        Returns:
            Step configuration dict with at least ``name`` and ``id`` set.
        """
        if step is None:
            step = {}
        # make name from setup function name if name is a function
        name = self.make_name_from_func(step_func)
        id_ = self.make_id_from_func(step_func)
        step_config: dict[str, Any] = {"name": name, "id": id_}
        if run is not None:
            step_config["run"] = run
        if uses is not None:
            step_config["uses"] = uses
        if if_condition is not None:
            step_config["if"] = if_condition
        if with_ is not None:
            step_config["with"] = with_
        if env is not None:
            step_config["env"] = env

        step_config.update(step)

        return step_config

    def make_name_from_func(self, func: Callable[..., Any]) -> str:
        """Generate a human-readable display name from a function.

        Splits the function name on underscores, capitalises each word, and
        strips the first word (the type prefix, e.g. ``job`` or ``step``).

        Args:
            func: The function whose name provides the source text.

        Returns:
            Display name with the prefix removed, e.g. ``"Build Artifacts"``
            from ``job_build_artifacts``.
        """
        name = make_name_from_obj(func, split_on="_", join_on=" ", capitalize=True)
        prefix = next(split_on_uppercase(name))
        return name.removeprefix(prefix).strip()

    def make_id_from_func(self, func: Callable[..., Any]) -> str:
        """Generate a compact identifier from a function name.

        Strips the first underscore-delimited segment (the type prefix, e.g.
        ``step`` or ``job``) and returns the rest as the identifier.

        Args:
            func: The function whose name provides the source text.

        Returns:
            Identifier string, e.g. ``"build_artifacts"`` from
            ``job_build_artifacts``.
        """
        name = func.__name__  # ty:ignore[unresolved-attribute]
        prefix = name.split("_")[0]
        return name.removeprefix(f"{prefix}_")

    # triggers
    def on_workflow_dispatch(self) -> dict[str, Any]:
        """Create a manual ``workflow_dispatch`` trigger.

        Returns:
            Trigger configuration that allows manually starting the workflow
            from the GitHub Actions UI or API.
        """
        return {"workflow_dispatch": {}}

    def on_push(self, branches: list[str] | None = None) -> dict[str, Any]:
        """Create a ``push`` trigger.

        Args:
            branches: Branches to trigger on.  Defaults to the default branch
                (``"main"``).

        Returns:
            Trigger configuration for push events.
        """
        if branches is None:
            branches = [VersionController.I.default_branch()]
        return {"push": {"branches": branches}}

    def on_schedule(self, cron: str) -> dict[str, Any]:
        """Create a scheduled ``cron`` trigger.

        Args:
            cron: Cron expression defining the schedule
                (e.g. ``"0 1 * * *"`` for 01:00 UTC daily).

        Returns:
            Trigger configuration for scheduled runs.
        """
        return {"schedule": [{"cron": cron}]}

    def on_pull_request(self, types: list[str] | None = None) -> dict[str, Any]:
        """Create a ``pull_request`` trigger.

        Args:
            types: Pull request event types to react to.  Defaults to
                ``["opened", "synchronize", "reopened"]``.

        Returns:
            Trigger configuration for pull request events.
        """
        if types is None:
            types = ["opened", "synchronize", "reopened"]
        return {"pull_request": {"types": types}}

    def on_workflow_run(
        self, workflows: list[str], branches: list[str] | None = None
    ) -> dict[str, Any]:
        """Create a ``workflow_run`` trigger.

        Args:
            workflows: Names of workflows whose completion triggers this
                workflow.
            branches: Optional branch filter.  When provided, only completions
                of the listed workflows on these branches fire the trigger.

        Returns:
            Trigger configuration for ``workflow_run`` events with
            ``types: [completed]``.
        """
        config: dict[str, Any] = {"workflows": workflows, "types": ["completed"]}
        if branches is not None:
            config["branches"] = branches
        return {"workflow_run": config}

    # Strategy
    def strategy_matrix_os_and_python_version(
        self,
        os: list[str] | None = None,
        python_version: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
        strategy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a strategy with OS and Python version matrix.

        Args:
            os: Runner labels to test against.  Defaults to Ubuntu, Windows,
                and macOS latest (``ubuntu-latest``, ``windows-latest``,
                ``macos-latest``).
            python_version: Python version strings to test against.  Defaults
                to all versions returned by
                :meth:`~pyrig.rig.configs.pyproject.PyprojectConfigFile.supported_python_versions`.
            matrix: Additional matrix dimensions to merge in.
            strategy: Additional strategy options (e.g. ``max-parallel``).

        Returns:
            Strategy configuration containing the combined OS and Python
            version matrix.
        """
        return self.strategy_matrix(
            matrix=self.matrix_os_and_python_version(
                os=os, python_version=python_version, matrix=matrix
            ),
            strategy=strategy,
        )

    def strategy_matrix_python_version(
        self,
        python_version: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
        strategy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a strategy with Python version matrix.

        Args:
            python_version: Python version strings to test against.  Defaults
                to all versions returned by
                :meth:`~pyrig.rig.configs.pyproject.PyprojectConfigFile.supported_python_versions`.
            matrix: Additional matrix dimensions to merge in.
            strategy: Additional strategy options (e.g. ``max-parallel``).

        Returns:
            Strategy configuration containing the Python version matrix.
        """
        return self.strategy_matrix(
            matrix=self.matrix_python_version(
                python_version=python_version, matrix=matrix
            ),
            strategy=strategy,
        )

    def strategy_matrix_os(
        self,
        os: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
        strategy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a strategy with OS matrix.

        Args:
            os: Runner labels to test against.  Defaults to Ubuntu, Windows,
                and macOS latest (``ubuntu-latest``, ``windows-latest``,
                ``macos-latest``).
            matrix: Additional matrix dimensions to merge in.
            strategy: Additional strategy options (e.g. ``max-parallel``).

        Returns:
            Strategy configuration containing the OS matrix.
        """
        return self.strategy_matrix(
            matrix=self.matrix_os(os=os, matrix=matrix), strategy=strategy
        )

    def strategy_matrix(
        self,
        *,
        strategy: dict[str, Any] | None = None,
        matrix: dict[str, list[Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a matrix strategy configuration.

        Args:
            strategy: Base strategy options.
            matrix: Matrix dimensions.

        Returns:
            Strategy configuration with matrix.
        """
        if strategy is None:
            strategy = {}
        if matrix is None:
            matrix = {}
        strategy["matrix"] = matrix
        return self.strategy(strategy=strategy)

    def strategy(
        self,
        *,
        strategy: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply defaults to a strategy configuration.

        Sets ``fail-fast`` to ``True`` if not already present in the
        strategy dict.

        Args:
            strategy: Strategy configuration to process.

        Returns:
            The strategy dict with ``fail-fast`` defaulting to ``True``.
        """
        strategy["fail-fast"] = strategy.pop("fail-fast", True)
        return strategy

    def matrix_os_and_python_version(
        self,
        os: list[str] | None = None,
        python_version: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a matrix with OS and Python version dimensions.

        Args:
            os: Runner labels to include.  Defaults to Ubuntu, Windows, and
                macOS latest (``ubuntu-latest``, ``windows-latest``,
                ``macos-latest``).
            python_version: Python version strings to include.  Defaults to
                all versions returned by
                :meth:`~pyrig.rig.configs.pyproject.PyprojectConfigFile.supported_python_versions`.
            matrix: Additional matrix dimensions to merge in.

        Returns:
            Matrix dict with ``os`` and ``python-version`` keys populated.
        """
        if matrix is None:
            matrix = {}
        os_matrix = self.matrix_os(os=os, matrix=matrix)["os"]
        python_version_matrix = self.matrix_python_version(
            python_version=python_version, matrix=matrix
        )["python-version"]
        matrix["os"] = os_matrix
        matrix["python-version"] = python_version_matrix
        return self.matrix(matrix=matrix)

    def matrix_os(
        self,
        *,
        os: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a matrix with OS dimension.

        Args:
            os: Runner labels to include.  Defaults to Ubuntu, Windows, and
                macOS latest (``ubuntu-latest``, ``windows-latest``,
                ``macos-latest``).
            matrix: Additional matrix dimensions to merge in.

        Returns:
            Matrix dict with the ``os`` key populated.
        """
        if os is None:
            os = [self.UBUNTU_LATEST, self.WINDOWS_LATEST, self.MACOS_LATEST]
        if matrix is None:
            matrix = {}
        matrix["os"] = os
        return self.matrix(matrix=matrix)

    def matrix_python_version(
        self,
        *,
        python_version: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a matrix with Python version dimension.

        Args:
            python_version: Python version strings to include.  Defaults to
                all versions returned by
                :meth:`~pyrig.rig.configs.pyproject.PyprojectConfigFile.supported_python_versions`.
            matrix: Additional matrix dimensions to merge in.

        Returns:
            Matrix dict with the ``python-version`` key populated.
        """
        if python_version is None:
            python_version = [
                str(v) for v in PyprojectConfigFile.I.supported_python_versions()
            ]
        if matrix is None:
            matrix = {}
        matrix["python-version"] = python_version
        return self.matrix(matrix=matrix)

    def matrix(self, matrix: dict[str, list[Any]]) -> dict[str, Any]:
        """Return the matrix configuration.

        This method is an extension point.  The base implementation returns the
        dict unchanged; subclasses can override it to apply transformations or
        add fixed dimensions to every matrix produced by this workflow.

        Args:
            matrix: Matrix dimensions dict to pass through.

        Returns:
            The matrix configuration, unchanged by default.
        """
        return matrix

    # WorkflowConfigFile Steps
    # ----------------------------------------------------------------------------
    # Combined Steps
    def steps_core_matrix_setup(
        self,
        *,
        no_dev: bool = False,
        python_version: str | None = None,
        repo_token: bool = False,
        patch_version: bool = False,
    ) -> list[dict[str, Any]]:
        """Build setup steps for matrix jobs.

        Delegates entirely to :meth:`steps_core_installed_setup`.  Using this
        method in matrix jobs makes the intent explicit and keeps a consistent
        naming pattern alongside the other ``steps_core_*`` helpers.

        Args:
            no_dev: Omit dev dependency groups from the sync.
            python_version: Python version string.  ``None`` resolves to the
                latest supported minor version.
            repo_token: Use ``REPO_TOKEN`` for checkout authentication.
            patch_version: Bump and stage the patch version as part of setup.

        Returns:
            Ordered list of step configuration dicts.
        """
        return [
            *self.steps_core_installed_setup(
                python_version=python_version,
                repo_token=repo_token,
                no_dev=no_dev,
                patch_version=patch_version,
            ),
        ]

    def steps_core_installed_setup(
        self,
        *,
        no_dev: bool = False,
        python_version: str | None = None,
        repo_token: bool = False,
        patch_version: bool = False,
    ) -> list[dict[str, Any]]:
        """Build setup steps that also update and install dependencies.

        Extends :meth:`steps_core_setup` with a dependency upgrade, a full
        ``uv sync``, and a git-add step for lock-file changes.

        Args:
            no_dev: Omit dev dependency groups from the sync.
            python_version: Python version string.  Defaults to the latest
                minor version supported by the project.
            repo_token: Use ``REPO_TOKEN`` for checkout authentication.
            patch_version: Bump and stage the patch version as part of setup.

        Returns:
            Ordered list of step configuration dicts.
        """
        return [
            *self.steps_core_setup(
                python_version=python_version,
                repo_token=repo_token,
                patch_version=patch_version,
            ),
            self.step_update_dependencies(),
            self.step_install_dependencies(no_dev=no_dev),
            self.step_add_dependency_updates_to_version_control(),
        ]

    def steps_core_setup(
        self,
        python_version: str | None = None,
        *,
        repo_token: bool = False,
        patch_version: bool = False,
    ) -> list[dict[str, Any]]:
        """Build the base checkout and environment setup steps.

        Checks out the repository, configures git credentials, and installs
        the package manager (uv) with the specified Python version.
        Optionally bumps the patch version and stages the change.

        Args:
            python_version: Python version string for uv.  Defaults to the
                latest minor version supported by the project.
            repo_token: Use ``REPO_TOKEN`` instead of the default token when
                checking out the repository.  Required when subsequent steps
                need to push changes back to the repository.
            patch_version: If ``True``, append a patch-version bump step and a
                git-add step for ``pyproject.toml`` and the lock file.

        Returns:
            Ordered list of step configuration dicts.
        """
        if python_version is None:
            python_version = str(
                PyprojectConfigFile.I.latest_possible_python_version(level="minor")
            )
        core = [
            self.step_checkout_repository(repo_token=repo_token),
            self.step_setup_version_control(),
            self.step_setup_package_manager(python_version=python_version),
        ]
        if patch_version:
            core = [
                *core,
                self.step_patch_version(),
                self.step_add_version_bump_to_version_control(),
            ]
        return core

    # Single Steps
    # ----------------------------------------------------------------------------

    def step_checkout_repository(
        self,
        *,
        step: dict[str, Any] | None = None,
        repo_token: bool = False,
    ) -> dict[str, Any]:
        """Build a step that checks out the repository.

        Uses ``actions/checkout@main``.  When ``repo_token`` is ``True``,
        the checkout authenticates with ``REPO_TOKEN`` instead of the default
        ``GITHUB_TOKEN``, which is required when subsequent steps need to push
        commits or tags back to the repository.

        Args:
            step: Additional keys to merge into the step configuration.
            repo_token: Authenticate with ``REPO_TOKEN`` to allow pushing from
                within the workflow.

        Returns:
            Step using ``actions/checkout@main``.
        """
        if step is None:
            step = {}
        if repo_token:
            step.setdefault("with", {})["token"] = self.insert_repo_token()
        return self.step(
            step_func=self.step_checkout_repository,
            uses="actions/checkout@main",
            step=step,
        )

    def step_setup_version_control(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that configures the git user identity.

        Sets ``user.email`` and ``user.name`` globally on the runner so that
        automated commits made during the workflow are attributed to
        ``github-actions[bot]``.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs two ``git config --global`` commands.
        """
        return self.step(
            step_func=self.step_setup_version_control,
            run=str(
                VersionController.I.config_global_user_email_args(
                    email='"github-actions[bot]@users.noreply.github.com"',
                ),
            )
            + " && "
            + str(
                VersionController.I.config_global_user_name_args(
                    name='"github-actions[bot]"'
                )
            ),
            step=step,
        )

    def step_setup_package_manager(
        self,
        *,
        python_version: str,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that installs uv and pins the Python version.

        Uses ``astral-sh/setup-uv`` to install uv on the runner and configure
        it to use the given Python version.  All subsequent ``uv run`` and
        ``uv sync`` commands will use this version.

        Args:
            python_version: Python version string to pin, e.g. ``"3.13"``.
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using ``astral-sh/setup-uv@main``.
        """
        return self.step(
            step_func=self.step_setup_package_manager,
            uses="astral-sh/setup-uv@main",
            with_={"python-version": python_version},
            step=step,
        )

    def step_patch_version(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that bumps the project patch version.

        Runs ``uv version --bump patch`` to increment the patch segment of the
        version string in ``pyproject.toml``.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that increments the patch version.
        """
        return self.step(
            step_func=self.step_patch_version,
            run=str(PackageManager.I.patch_version_args()),
            step=step,
        )

    def step_add_version_bump_to_version_control(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that stages the version-bump files.

        Stages ``pyproject.toml`` and the lock file so they are included in
        the next commit step.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``git add pyproject.toml uv.lock``.
        """
        return self.step(
            step_func=self.step_add_version_bump_to_version_control,
            run=str(VersionController.I.add_pyproject_toml_and_lock_file_args()),
            step=step,
        )

    def step_update_dependencies(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that upgrades all pinned dependencies.

        Runs ``uv lock --upgrade`` to update the lock file to the latest
        versions allowed by the version constraints in ``pyproject.toml``.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``uv lock --upgrade``.
        """
        return self.step(
            step_func=self.step_update_dependencies,
            run=str(PackageManager.I.update_dependencies_args()),
            step=step,
        )

    def step_install_dependencies(
        self,
        *,
        no_dev: bool = False,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that synchronises the virtual environment.

        Runs ``uv sync`` to install all locked dependencies.  Pass
        ``no_dev=True`` to omit the dev dependency group, which is useful for
        production builds where dev tools are not needed.

        Args:
            no_dev: Exclude the dev dependency group from the sync.
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``uv sync`` (with ``--no-group dev`` when
            ``no_dev`` is ``True``).
        """
        install = str(PackageManager.I.install_dependencies_args())
        if no_dev:
            install += " --no-group dev"
        run = install

        return self.step(
            step_func=self.step_install_dependencies,
            run=run,
            step=step,
        )

    def step_add_dependency_updates_to_version_control(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that stages dependency file changes.

        Stages ``pyproject.toml`` and the lock file after a dependency update
        so the changes are included in the next commit.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``git add pyproject.toml uv.lock``.
        """
        return self.step(
            step_func=self.step_add_dependency_updates_to_version_control,
            run=str(VersionController.I.add_pyproject_toml_and_lock_file_args()),
            step=step,
        )

    def step_run_pre_commit_hooks(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that runs all pre-commit hooks via prek.

        Runs ``prek --all-files`` to enforce code quality checks across the
        entire working tree.  Including this step also ensures that
        ``git stash pop`` does not fail when there are no staged changes,
        since prek leaves the working tree clean.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``uv run prek --all-files``.
        """
        return self.step(
            step_func=self.step_run_pre_commit_hooks,
            run=str(PackageManager.I.run_args(*PreCommitter.I.run_all_files_args())),
            step=step,
        )

    def step_run_dependency_audit(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that audits dependencies for known vulnerabilities.

        Runs ``pip-audit`` via uv against the installed environment to detect
        CVEs in direct and transitive dependencies.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``uv run pip-audit``.
        """
        return self.step(
            step_func=self.step_run_dependency_audit,
            run=str(PackageManager.I.run_args(*DependencyAuditor.I.audit_args())),
            step=step,
        )

    def step_run_tests(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that runs the test suite with pytest.

        When running inside the pyrig package itself
        (``src_package_is_pyrig()`` is ``True``), the ``REPO_TOKEN``
        environment variable is injected so that tests that interact with the
        GitHub API have the required credentials.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that executes pytest with CI-appropriate flags.
        """
        if step is None:
            step = {}
        if src_package_is_pyrig():
            step.setdefault("env", {})[RemoteVersionController.I.access_token_key()] = (
                self.insert_repo_token()
            )
        run = str(PackageManager.I.run_args(*ProjectTester.I.run_tests_in_ci_args()))
        return self.step(
            step_func=self.step_run_tests,
            run=run,
            step=step,
        )

    def step_upload_coverage_report(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that uploads the coverage report to Codecov.

        Requires a Codecov account linked to the repository (log in at
        codecov.io with GitHub).

        - **Private repos**: ``CODECOV_TOKEN`` secret is required.
        - **Public repos**: ``CODECOV_TOKEN`` is recommended.  Tokenless
          upload can be enabled in Codecov settings (Settings > General).

        When ``CODECOV_TOKEN`` is not configured, ``fail_ci_if_error`` is set
        to ``false`` so a missing token does not break the CI run.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using ``codecov/codecov-action@main``.
        """
        #  make fail_ci_if_error true if token exists and false if it doesn't
        fail_ci_if_error = self.insert_var(
            f"{self.codecov_token_var()} && 'true' || 'false'"
        )
        return self.step(
            step_func=self.step_upload_coverage_report,
            uses="codecov/codecov-action@main",
            with_={
                "files": "coverage.xml",
                "token": self.insert_codecov_token(),
                "fail_ci_if_error": fail_ci_if_error,
            },
            step=step,
        )

    def step_build_wheel(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that packages the project as a Python wheel.

        Runs ``uv build`` to produce wheel and sdist distributions in the
        ``dist/`` directory.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``uv build``.
        """
        return self.step(
            step_func=self.step_build_wheel,
            run=str(PackageManager.I.build_args()),
            step=step,
        )

    def step_build_artifacts(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that runs the pyrig build command.

        Invokes ``pyrig build`` via uv, which delegates to all registered
        concrete :class:`~pyrig.rig.builders.base.builder.BuilderConfigFile`
        subclasses to produce their respective artifacts.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``uv run pyrig build``.
        """
        return self.step(
            step_func=self.step_build_artifacts,
            run=str(PackageManager.I.run_args(*Pyrigger.I.cmd_args(cmd=build))),
            step=step,
        )

    def step_install_container_engine(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that installs Podman as the container engine.

        Uses the ``redhat-actions/podman-install`` GitHub Action.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that installs Podman on the runner.
        """
        return self.step(
            step_func=self.step_install_container_engine,
            uses="redhat-actions/podman-install@main",
            with_={"github-token": self.insert_github_token()},
            step=step,
        )

    def step_build_container_image(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that creates the project container image.

        Runs the container engine build command derived from
        :meth:`~pyrig.rig.tools.container_engine.ContainerEngine.build_args`.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that builds the container image from the project's
            Containerfile.
        """
        return self.step(
            step_func=self.step_build_container_image,
            run=str(
                ContainerEngine.I.build_args(
                    project_name=PackageManager.I.project_name()
                )
            ),
            step=step,
        )

    def step_save_container_image(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that exports the container image to a tar archive.

        The archive is written to ``dist/<project-name>.tar`` so it can be
        uploaded as a workflow artifact.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that saves the container image using the container engine's
            save command.
        """
        image_file = Path(f"{PackageManager.I.project_name()}.tar")
        image_path = Path(BuilderConfigFile.dist_dir_name()) / image_file
        return self.step(
            step_func=self.step_save_container_image,
            run=str(
                ContainerEngine.I.save_args(
                    image_path=image_path,
                )
            ),
            step=step,
        )

    def step_build_documentation(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that generates the MkDocs documentation site.

        Runs the docs builder command, which invokes ``mkdocs build`` and
        writes the rendered HTML site to the ``site/`` directory.  The
        ``site/`` directory is then consumed by the subsequent
        :meth:`step_upload_documentation` step.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs the docs builder command.
        """
        return self.step(
            step_func=self.step_build_documentation,
            run=str(PackageManager.I.run_args(*DocsBuilder.I.build_args())),
            step=step,
        )

    def step_enable_pages(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that enables GitHub Pages for the repository.

        Calls ``actions/configure-pages`` with ``enablement: true``.  This is
        idempotent -- running it on a repository where Pages is already enabled
        has no effect.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that enables GitHub Pages using ``REPO_TOKEN``.
        """
        return self.step(
            step_func=self.step_enable_pages,
            uses="actions/configure-pages@main",
            with_={"token": self.insert_repo_token(), "enablement": "true"},
            step=step,
        )

    def step_upload_documentation(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that uploads the documentation as a Pages artifact.

        Uploads the ``site/`` directory produced by
        :meth:`step_build_documentation` so that the Pages deployment step
        can publish it.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using ``actions/upload-pages-artifact@main``.
        """
        return self.step(
            step_func=self.step_upload_documentation,
            uses="actions/upload-pages-artifact@main",
            with_={"path": "site"},
            step=step,
        )

    def step_deploy_documentation(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that deploys the uploaded Pages artifact to GitHub Pages.

        Must be preceded by :meth:`step_upload_documentation`.  The job that
        contains this step must have ``pages: write`` and
        ``id-token: write`` permissions.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using ``actions/deploy-pages@main``.
        """
        return self.step(
            step_func=self.step_deploy_documentation,
            uses="actions/deploy-pages@main",
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
            Step using ``release-changelog-builder-action@develop``.
        """
        return self.step(
            step_func=self.step_build_changelog,
            uses="mikepenz/release-changelog-builder-action@develop",
            with_={"token": self.insert_github_token()},
            step=step,
        )

    def step_extract_version(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that writes the current version to ``GITHUB_OUTPUT``.

        Evaluates :meth:`insert_version` (``v$(uv version --short)``) at
        runtime and appends ``version=v<x.y.z>`` to the ``$GITHUB_OUTPUT``
        file.  Downstream steps can reference the value via
        :meth:`insert_version_from_extract_version_step`.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that exports the version as a GitHub Actions output.
        """
        return self.step(
            step_func=self.step_extract_version,
            run=f'echo "version={self.insert_version()}" >> $GITHUB_OUTPUT',
            step=step,
        )

    def step_create_release(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that creates a GitHub release.

        Uses ``ncipollo/release-action`` to create a release tagged with the
        version extracted by :meth:`step_extract_version`.  Attaches all
        files under ``dist/`` as release assets and uses the changelog
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
                "name": f"{self.insert_repository_name()} {version}",
                "body": self.insert_changelog(),
                "artifacts": f"{BuilderConfigFile.dist_dir_name()}/*",
            },
            step=step,
        )

    def step_publish_to_pypi(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that publishes the wheel to PyPI.

        The publish command is wrapped in a shell conditional: if
        ``PYPI_TOKEN`` is configured the step runs ``uv publish``; otherwise
        it prints a skip message and exits successfully.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that conditionally publishes to PyPI using ``PYPI_TOKEN``.
        """
        run = str(PackageManager.I.publish_args(token=self.insert_pypi_token()))
        run_if = self.run_if_condition(run, self.pypi_token_var())
        return self.step(
            step_func=self.step_publish_to_pypi,
            run=run_if,
            step=step,
        )

    def step_create_and_push_tag(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that creates and pushes a version tag.

        Creates a tag named ``v<version>`` (e.g. ``v1.2.3``) and pushes it to
        the remote.  The version string is resolved at runtime via
        :meth:`insert_version`.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``git tag`` followed by
            ``git push origin <tag>``.
        """
        return self.step(
            step_func=self.step_create_and_push_tag,
            run=str(VersionController.I.tag_args(tag=self.insert_version()))
            + " && "
            + str(VersionController.I.push_origin_tag_args(tag=self.insert_version())),
            step=step,
        )

    def step_commit_added_changes(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that commits any staged changes.

        Commits with the message
        ``[skip ci] CI/CD: Committing possible staged changes`` and uses
        ``--no-verify`` to bypass pre-commit hooks.  The ``[skip ci]`` prefix
        prevents the commit from re-triggering the workflow.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``git commit --no-verify``.
        """
        msg = '"[skip ci] CI/CD: Committing possible staged changes"'
        return self.step(
            step_func=self.step_commit_added_changes,
            run=str(VersionController.I.commit_no_verify_args(msg=msg)),
            step=step,
        )

    def step_push_commits(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that pushes the current branch to the remote.

        Pushes any commits staged during the workflow (such as version bumps
        or lock-file updates) to the remote origin.  The repository must be
        checked out with ``REPO_TOKEN`` via
        :meth:`step_checkout_repository` (``repo_token=True``) for this push
        to succeed.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs ``git push``.
        """
        return self.step(
            step_func=self.step_push_commits,
            run=str(VersionController.I.push_args()),
            step=step,
        )

    def step_protect_repository(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that applies repository protection rules.

        Runs ``pyrig protect-repo`` via uv with the ``REPO_TOKEN`` secret,
        which configures GitHub branch protection and other repository settings
        defined in ``branch-protection.json``.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that runs the protect-repo command with ``REPO_TOKEN``
            injected as an environment variable.
        """
        return self.step(
            step_func=self.step_protect_repository,
            run=str(PackageManager.I.run_args(*Pyrigger.I.cmd_args(cmd=protect_repo))),
            env={
                RemoteVersionController.I.access_token_key(): self.insert_repo_token()
            },
            step=step,
        )

    def step_upload_artifacts(
        self,
        *,
        name: str | None = None,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that uploads build artifacts.

        Uploads the entire ``dist/`` directory as a named GitHub Actions
        artifact so it can be downloaded by downstream jobs or workflow runs.

        Args:
            name: Artifact name.  Defaults to ``<project>-<runner.os>``.
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using ``actions/upload-artifact@main``.
        """
        if name is None:
            name = self.insert_artifact_name()
        return self.step(
            step_func=self.step_upload_artifacts,
            uses="actions/upload-artifact@main",
            with_={"name": name, "path": BuilderConfigFile.dist_dir_name()},
            step=step,
        )

    def step_download_artifacts_from_workflow_run(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that downloads artifacts from the triggering workflow run.

        Uses ``github.event.workflow_run.id`` as the run ID so it always
        fetches artifacts from the specific run that triggered the current
        workflow, even when multiple runs exist.  All per-OS artifact
        directories are merged into a single ``dist/`` directory
        (``merge-multiple: true``).

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step using ``actions/download-artifact@main`` with the workflow
            run ID and a GitHub token for cross-workflow artifact access.
        """
        with_: dict[str, Any] = {
            "path": BuilderConfigFile.dist_dir_name(),
            "run-id": self.insert_workflow_run_id(),
            "github-token": self.insert_github_token(),
        }

        with_["merge-multiple"] = "true"
        return self.step(
            step_func=self.step_download_artifacts_from_workflow_run,
            uses="actions/download-artifact@main",
            with_=with_,
            step=step,
        )

    def step_opt_out_of_workflow(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step that marks the workflow as opted out.

        Used by :meth:`is_correct` to replace all job steps when a workflow
        file is intentionally left empty, keeping the YAML valid while
        effectively disabling the workflow.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that echoes an opt-out message using the workflow name.
        """
        return self.step(
            step_func=self.step_opt_out_of_workflow,
            run=f"echo 'Opting out of {self.workflow_name()} workflow.'",
            step=step,
        )

    def step_aggregate_jobs(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a fan-in step used to aggregate matrix job results.

        Downstream jobs declare a ``needs`` dependency on the job that contains
        this step, ensuring all matrix runners have finished before continuing.

        Args:
            step: Additional keys to merge into the step configuration.

        Returns:
            Step that echoes an aggregation message.
        """
        return self.step(
            step_func=self.step_aggregate_jobs,
            run="echo 'Aggregating jobs into one job.'",
            step=step,
        )

    # Variables
    # ----------------------------------------------------------------------------

    def repo_token_var(self) -> str:
        """Get the raw secrets expression for ``REPO_TOKEN``.

        Returns:
            ``"secrets.REPO_TOKEN"``
        """
        return self.secrets_var(RemoteVersionController.I.access_token_key())

    def github_token_var(self) -> str:
        """Get the raw secrets expression for ``GITHUB_TOKEN``.

        Returns:
            ``"secrets.GITHUB_TOKEN"``
        """
        return self.secrets_var("GITHUB_TOKEN")

    def codecov_token_var(self) -> str:
        """Get the raw secrets expression for ``CODECOV_TOKEN``.

        Returns:
            ``"secrets.CODECOV_TOKEN"``
        """
        return self.secrets_var(ProjectCoverageTester.I.access_token_key())

    def pypi_token_var(self) -> str:
        """Get the raw secrets expression for ``PYPI_TOKEN``.

        Returns:
            ``"secrets.PYPI_TOKEN"``
        """
        return self.secrets_var(PackageIndex.I.access_token_key())

    def secrets_var(self, name: str) -> str:
        """Build the raw GitHub secrets expression for a secret name.

        Args:
            name: The secret's key name (e.g. ``"REPO_TOKEN"``).

        Returns:
            Raw expression string ``"secrets.<name>"`` suitable for use
            inside ``${{ ... }}`` wrappers.
        """
        return f"secrets.{name}"

    # Insertions
    # ----------------------------------------------------------------------------
    def insert_repo_token(self) -> str:
        """Get the ``${{ secrets.REPO_TOKEN }}`` expression.

        Returns:
            GitHub Actions expression for the ``REPO_TOKEN`` secret.
        """
        return self.insert_var(self.repo_token_var())

    def insert_pypi_token(self) -> str:
        """Get the ``${{ secrets.PYPI_TOKEN }}`` expression.

        Returns:
            GitHub Actions expression for the ``PYPI_TOKEN`` secret.
        """
        return self.insert_var(self.pypi_token_var())

    def insert_version(self) -> str:
        """Build the shell expression that resolves to the project version.

        Evaluates ``uv version --short`` in a subshell and prepends ``v``,
        so the result at workflow execution time is a string like ``v1.2.3``.

        Returns:
            Shell expression string, e.g. ``"v$(uv version --short)"``.
        """
        script = str(PackageManager.I.version_short_args())
        return f"v$({script})"

    def insert_version_from_extract_version_step(self) -> str:
        """Get the expression that reads the version from the extract step output.

        References the ``version`` output produced by
        :meth:`step_extract_version` so that subsequent steps can consume the
        resolved version string.

        Returns:
            GitHub Actions expression for
            ``steps.extract_version.outputs.version``.
        """
        # make dynamic with self.make_id_from_func(self.step_extract_version)
        return self.insert_var(
            f"steps.{self.make_id_from_func(self.step_extract_version)}.outputs.version"
        )

    def insert_changelog(self) -> str:
        """Get the expression that reads the changelog from the build step output.

        References the ``changelog`` output produced by
        :meth:`step_build_changelog`.

        Returns:
            GitHub Actions expression for
            ``steps.build_changelog.outputs.changelog``.
        """
        return self.insert_var(
            f"steps.{self.make_id_from_func(self.step_build_changelog)}.outputs.changelog"
        )

    def insert_github_token(self) -> str:
        """Get the ``${{ secrets.GITHUB_TOKEN }}`` expression.

        Returns:
            GitHub Actions expression for the automatic ``GITHUB_TOKEN``
            secret.
        """
        return self.insert_var(self.github_token_var())

    def insert_codecov_token(self) -> str:
        """Get the ``${{ secrets.CODECOV_TOKEN }}`` expression.

        Returns:
            GitHub Actions expression for the ``CODECOV_TOKEN`` secret.
        """
        return self.insert_var(self.codecov_token_var())

    def insert_repository_name(self) -> str:
        """Get the expression that resolves to the repository name.

        Returns:
            GitHub Actions expression for
            ``github.event.repository.name``.
        """
        return self.insert_var("github.event.repository.name")

    def insert_workflow_run_id(self) -> str:
        """Get the expression that resolves to the triggering workflow run ID.

        Resolves to the run ID of the workflow that triggered the current
        workflow via a ``workflow_run`` event.  Used when downloading
        artifacts from that specific run.

        Returns:
            GitHub Actions expression for
            ``github.event.workflow_run.id``.
        """
        return self.insert_var("github.event.workflow_run.id")

    def insert_os(self) -> str:
        """Get the expression that resolves to the current runner OS name.

        Returns:
            GitHub Actions expression for ``runner.os`` (e.g. ``"Linux"``,
            ``"Windows"``, ``"macOS"``).
        """
        return self.insert_var("runner.os")

    def insert_matrix_os(self) -> str:
        """Get the expression that resolves to the current matrix OS value.

        Returns:
            GitHub Actions expression for ``matrix.os``.
        """
        return self.insert_var("matrix.os")

    def insert_matrix_python_version(self) -> str:
        """Get the expression that resolves to the current matrix Python version.

        Returns:
            GitHub Actions expression for ``matrix.python-version``.
        """
        return self.insert_var("matrix.python-version")

    def insert_artifact_name(self) -> str:
        """Build the default artifact name for the current runner OS.

        Returns:
            Artifact name in the format ``"<project-name>-<runner.os>"``,
            where ``<runner.os>`` is resolved at workflow execution time.
        """
        return f"{PackageManager.I.project_name()}-{self.insert_os()}"

    def insert_var(self, var: str) -> str:
        """Wrap an expression in GitHub Actions ``${{ ... }}`` syntax.

        This is the primitive used by all ``insert_*`` methods.

        Args:
            var: The raw expression to wrap
                (e.g. ``"secrets.REPO_TOKEN"``).

        Returns:
            The expression surrounded by ``${{ }}`` delimiters, e.g.
            ``"${{ secrets.REPO_TOKEN }}"``.
        """
        return f"${{{{ {var} }}}}"

    # ifs
    # ----------------------------------------------------------------------------
    def combined_if(self, *conditions: str, operator: str) -> str:
        """Combine multiple GitHub Actions expressions with a logical operator.

        Strips any existing ``${{ }}`` wrappers from each condition, joins
        them with the given operator, and re-wraps the result.

        Args:
            *conditions: Individual condition expressions, with or without
                ``${{ }}`` wrappers.
            operator: Logical operator to join conditions,
                e.g. ``"&&"`` or ``"||"``.

        Returns:
            Single GitHub Actions expression combining all conditions.
        """
        bare_conditions = [
            condition.strip().removeprefix("${{").removesuffix("}}").strip()
            for condition in conditions
        ]
        return self.insert_var(f" {operator} ".join(bare_conditions))

    def if_workflow_run_is_success(self) -> str:
        """Build a condition that is true when the triggering workflow run succeeded.

        Returns:
            GitHub Actions expression checking
            ``github.event.workflow_run.conclusion == 'success'``.
        """
        return self.insert_var("github.event.workflow_run.conclusion == 'success'")

    def if_workflow_run_is_not_cron_triggered(self) -> str:
        """Build a condition that is true when the triggering run was not scheduled.

        Returns:
            GitHub Actions expression checking
            ``github.event.workflow_run.event != 'schedule'``.
        """
        return self.insert_var("github.event.workflow_run.event != 'schedule'")

    def if_pypi_token_configured(self) -> str:
        """Build a condition that is true when ``PYPI_TOKEN`` is configured.

        Returns:
            GitHub Actions expression checking
            ``secrets.PYPI_TOKEN != ''``.
        """
        return self.insert_var(f"{self.pypi_token_var()} != ''")

    # Runs
    # ----------------------------------------------------------------------------
    def run_if_condition(self, run: str, condition: str) -> str:
        """Build a shell command that runs conditionally.

        Wraps ``run`` in a bash ``if`` statement: if the evaluated condition
        is truthy the command executes; otherwise a skip message is echoed
        and the step exits successfully.  This avoids failing a job when an
        optional secret (e.g. ``PYPI_TOKEN``) is not configured.

        Args:
            run: The shell command to execute when the condition is met.
            condition: A raw GitHub expression (without ``${{ }}`` wrappers).

        Returns:
            A bash snippet:
            ``if [ ${{ <condition> }} ]; then <run>; else echo "Skipping..."; fi``.
        """
        condition_check = self.insert_var(condition)
        # make a script that runs the command if the token is configured
        # and echos a message if it is not
        condition_as_str = (
            condition_check.strip().removeprefix("${{").removesuffix("}}").strip()
        )
        msg = f"Skipping step due to failed condition: {condition_as_str}."
        return f'if [ {condition_check} ]; then {run}; else echo "{msg}"; fi'
