"""GitHub Actions workflow YAML generation utilities and abstract base classes."""

from abc import abstractmethod
from pathlib import Path
from types import MethodType
from typing import Any

from pyrig_runtime.core.strings import snake_to_kebab_case

from pyrig.core.strings import (
    reformat_name,
    split_on_uppercase,
)
from pyrig.rig.configs.base.yaml import YMLDictConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.linting.shell import ShellLinter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.programming_language import ProgrammingLanguage
from pyrig.rig.tools.version_control.controller import VersionController
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class WorkflowConfigFile(YMLDictConfigFile):
    """Abstract base class for generating GitHub Actions workflow YAML files.

    Subclasses define a workflow by implementing `jobs` and optionally
    overriding the trigger, default, and environment methods. The base class
    provides composable building blocks for jobs, steps, strategies,
    triggers, and expression helpers so subclasses can assemble complete
    workflows without writing raw YAML. Workflows deny all `GITHUB_TOKEN`
    permissions by default; jobs that check out the repository must explicitly
    request `self.permission_contents()` (or a broader permission when
    required).

    Attributes:
        UBUNTU_LATEST: Runner label for Ubuntu (`"ubuntu-latest"`).
        WINDOWS_LATEST: Runner label for Windows (`"windows-latest"`).
        MACOS_LATEST: Runner label for macOS (`"macos-latest"`).

    Example:
        >>> from pyrig.rig.configs.base.workflow import WorkflowConfigFile
        >>>
        >>> class MyWorkflowConfigFile(WorkflowConfigFile):
        ...     def jobs(self) -> dict[str, Any]:
        ...         return self.job(
        ...             self.jobs,
        ...             permissions=self.permission_contents(),
        ...             steps=self.steps_core_installed_setup(),
        ...         )
        ...
        ...     def workflow_triggers(self) -> dict[str, Any]:
        ...         return {**self.on_workflow_dispatch(), **self.on_push()}
    """

    UBUNTU_LATEST = "ubuntu-latest"
    WINDOWS_LATEST = "windows-latest"
    MACOS_LATEST = "macos-latest"

    @abstractmethod
    def jobs(self) -> dict[str, Any]:
        """Return the jobs that make up this workflow.

        Returns:
            Dict mapping job IDs to their configurations.
        """

    @abstractmethod
    def workflow_triggers(self) -> dict[str, Any]:
        """Return the events that trigger this workflow.

        Build the dict from the `on_*` trigger helpers, e.g.
        `on_workflow_dispatch()` for manual runs or `on_push()` for
        pushes to the default branch.

        Returns:
            Dict of trigger configurations.
        """

    def _configs(self) -> dict[str, Any]:
        """Assemble the complete workflow configuration dict.

        Returns:
            Top-level workflow configuration with `name`, `on`,
            `permissions`, `concurrency`, `defaults`, `env`, `run-name`, and
            `jobs` keys populated from the overridable methods. The default
            permissions policy denies all `GITHUB_TOKEN` access.
        """
        return {
            "name": self.workflow_name(),
            "on": self.workflow_triggers(),
            "permissions": self.permissions(),
            "concurrency": self.concurrency(),
            "defaults": self.defaults(),
            "env": self.global_env(),
            "run-name": self.run_name(),
            "jobs": self.jobs(),
        }

    def permissions(self) -> dict[str, Any]:
        """Return the workflow's default `GITHUB_TOKEN` permissions.

        Denies all permissions by default so that jobs receive no token
        access unless they explicitly declare what they need, rather than
        relying on the ambient repository/organization default (which is
        not visible from the workflow file and can be broader than expected).

        Returns:
            Empty dict, denying every permission.
        """
        return {}

    def permission_contents(self, *, write: bool = False) -> dict[str, str]:
        """Return the permission needed to read or write repository contents.

        Args:
            write: Whether the permission should be write (`True`) or read (`False`).

        Returns:
            Dict with the "contents" permission set to either "write" or "read".
        """
        return self.permission("contents", write=write)

    def permission_id_token(self, *, write: bool = False) -> dict[str, str]:
        """Return the permission needed to mint an OIDC token.

        Args:
            write: Whether the permission should be write (`True`) or read (`False`).

        Returns:
            Dict with the "id-token" permission set to either "write" or "read".
        """
        return self.permission("id-token", write=write)

    def permission_pages(self, *, write: bool = False) -> dict[str, str]:
        """Return the permission needed to deploy to GitHub Pages, optionally as write.

        Args:
            write: Whether the permission should be write (`True`) or read (`False`).

        Returns:
            Dict with the "pages" permission set to either "write" or "read".
        """
        return self.permission("pages", write=write)

    def permission_packages(self, *, write: bool = False) -> dict[str, str]:
        """Return the permission needed to read or write GitHub Packages.

        Args:
            write: Whether the permission should be write (`True`) or read (`False`).

        Returns:
            Dict with the "packages" permission set to either "write" or "read".
        """
        return self.permission("packages", write=write)

    def permission(self, name: str, *, write: bool = False) -> dict[str, str]:
        """Return a permission dictionary for the given permission name.

        Args:
            name: The name of the permission.
            write: Whether the permission should be write (`True`) or read (`False`).

        Returns:
            Dict with the permission name mapped to either "write" or "read".
        """
        return {name: "write" if write else "read"}

    def concurrency(self) -> dict[str, Any]:
        """Return the workflow's concurrency setting.

        Groups runs by workflow and ref so that superseded runs are queued
        or cancelled instead of running redundantly alongside newer ones.

        Returns:
            Dict of concurrency settings.
        """
        return {
            "group": self.insert_github_workflow_and_ref(),
            "cancel-in-progress": self.concurrency_cancel_in_progress(),
        }

    def concurrency_cancel_in_progress(self) -> bool:
        """Return whether superseded runs of this workflow should be cancelled.

        Override to `False` for workflows that mutate external state (e.g.
        publishing a release or package) and therefore shouldn't be
        interrupted mid-run; such runs are still serialized via the shared
        concurrency group, just not cancelled.

        Returns:
            `True` by default.
        """
        return True

    def parent_path(self) -> Path:
        """Return the GitHub Actions workflows directory."""
        return RemoteVersionController.I.config_dir() / "workflows"

    def defaults(self) -> dict[str, Any]:
        """Return the default settings applied to every step in the workflow.

        Returns:
            Dict of default settings.
        """
        return {"run": {"shell": ShellLinter.I.dialect()}}

    def global_env(self) -> dict[str, Any]:
        """Return environment variables applied to every job in the workflow.

        Override to add custom variables. By default sets a variable that
        prevents Python from writing `.pyc` bytecode files and a variable
        that prevents `uv` from auto-syncing the environment before commands.

        Returns:
            Dict of environment variable names to their values.
        """
        return {
            ProgrammingLanguage.I.no_bytecode_env_var(): 1,
            PackageManager.I.no_auto_install_env_var(): 1,
        }

    def workflow_name(self) -> str:
        """Derive a human-readable name from the class name.

        Removes the `WorkflowConfigFile` suffix and splits the remainder on
        uppercase letters to produce a space-separated title.

        Returns:
            Workflow name, e.g. `"Health Check"` for
            `HealthCheckWorkflowConfigFile`.
        """
        name = self.__class__.__name__.removesuffix(WorkflowConfigFile.__name__)
        return " ".join(split_on_uppercase(name))

    def run_name(self) -> str:
        """Return the display name shown for individual workflow runs.

        Override to customize. Defaults to `workflow_name`.

        Returns:
            The run name.
        """
        return self.workflow_name()

    def job(  # noqa: PLR0913
        self,
        method: MethodType,
        *,
        needs: list[str] | None = None,
        strategy: dict[str, Any] | None = None,
        permissions: dict[str, Any] | None = None,
        runs_on: str = UBUNTU_LATEST,
        if_condition: str | None = None,
        steps: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Build a job configuration dict.

        Args:
            method: Method representing this job; its name is used to derive
                the job ID.
            needs: IDs of jobs that must complete before this job starts.
            strategy: Matrix or other strategy configuration.
            permissions: Job-level permissions override.
            runs_on: Runner label. Defaults to `ubuntu-latest`.
            if_condition: GitHub Actions conditional expression controlling
                whether the job runs.
            steps: Ordered list of step configurations.

        Returns:
            Dict mapping the derived job ID to its configuration.
        """
        job_id = self.job_id_from_method(method)
        job = {"name": self.name_from_id(job_id)}
        if permissions is not None:
            job["permissions"] = permissions
        if if_condition is not None:
            job["if"] = if_condition
        if needs is not None:
            job["needs"] = needs
        job["runs-on"] = runs_on
        if strategy is not None:
            job["strategy"] = strategy
        if steps is not None:
            job["steps"] = steps
        return {job_id: job}

    def step(  # noqa: PLR0913
        self,
        method: MethodType,
        *,
        run: str | None = None,
        if_condition: str | None = None,
        uses: str | None = None,
        with_: dict[str, Any] | None = None,
        env: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step configuration dict.

        Args:
            method: Method representing this step; its name is used to
                derive the step `name` and `id` fields.
            run: Shell command to execute.
            if_condition: GitHub Actions conditional expression controlling
                whether the step runs.
            uses: GitHub Action reference to use (e.g.
                `"actions/checkout@main"`).
            with_: Input parameters passed to the action.
            env: Step-level environment variables.

        Returns:
            Step configuration dict with at least `name` and `id` set.
        """
        id_ = self.step_id_from_method(method)
        step = {
            "name": self.name_from_id(id_),
            "id": id_,
        }
        if if_condition is not None:
            step["if"] = if_condition
        if run is not None:
            step["run"] = run
        if uses is not None:
            step["uses"] = uses
        if with_ is not None:
            step["with"] = with_
        if env is not None:
            step["env"] = env

        return step

    def name_from_id(self, id_: str) -> str:
        """Generate a human-readable display name from a kebab-case identifier.

        Splits the identifier on hyphens and capitalizes each word.

        Args:
            id_: The kebab-case identifier to convert, e.g. one produced by
                `job_id_from_method()` or `step_id_from_method()`.

        Returns:
            Display name, e.g. `"Do Something"` from `"do-something"`.
        """
        return reformat_name(
            id_,
            split_on="-",
            join_on=" ",
            capitalize=True,
        )

    def job_id_from_method(self, method: MethodType) -> str:
        """Generate a job identifier from a `job_*` method name.

        Args:
            method: The job method whose name provides the source text.

        Returns:
            Identifier string in kebab-case, e.g. `"do-something"` from
            `job_do_something`.
        """
        return self.id_from_method(method, prefix=self.job.__name__)

    def step_id_from_method(self, method: MethodType) -> str:
        """Generate a step identifier from a `step_*` method name.

        Args:
            method: The step method whose name provides the source text.

        Returns:
            Identifier string in kebab-case, e.g. `"do-something"` from
            `step_do_something`.
        """
        return self.id_from_method(method, prefix=self.step.__name__)

    def id_from_method(self, method: MethodType, prefix: str) -> str:
        """Generate a compact identifier from a method name.

        Strips the given prefix (plus the underscore joining it to the rest
        of the name) and returns the rest in kebab-case.

        Args:
            method: The method whose name provides the source text.
            prefix: The leading segment to strip, e.g. `"job"` or `"step"`.

        Returns:
            Identifier string in kebab-case, e.g. `"do-something"` from
            `job_do_something` with `prefix="job"`.
        """
        return snake_to_kebab_case(method.__name__.removeprefix(f"{prefix}_"))

    def on_push(self, branches: list[str] | None = None) -> dict[str, Any]:
        """Create a `push` trigger.

        Args:
            branches: Branches to trigger on. Defaults to the default branch
                (`"main"`).

        Returns:
            Trigger configuration for push events.
        """
        if branches is None:
            branches = [VersionController.I.default_branch()]
        return {"push": {"branches": branches}}

    def on_schedule(self, cron: str) -> dict[str, Any]:
        """Create a scheduled `cron` trigger.

        Args:
            cron: Cron expression defining the schedule
                (e.g. `"0 1 * * *"` for 01:00 UTC daily).

        Returns:
            Trigger configuration for scheduled runs.
        """
        return {"schedule": [{"cron": cron}]}

    def on_pull_request(self, types: list[str] | None = None) -> dict[str, Any]:
        """Create a `pull_request` trigger.

        Args:
            types: Pull request event types to react to. Defaults to
                `["opened", "synchronize", "reopened"]`.

        Returns:
            Trigger configuration for pull request events.
        """
        if types is None:
            types = ["opened", "synchronize", "reopened"]
        return {"pull_request": {"types": types}}

    def on_workflow_run(
        self,
        workflows: list[str],
        branches: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a `workflow_run` trigger.

        Args:
            workflows: Names of workflows whose completion triggers this
                workflow.
            branches: Optional branch filter. When provided, only completions
                of the listed workflows on these branches fire the trigger.

        Returns:
            Trigger configuration for `workflow_run` events with
            `types: [completed]`.
        """
        configs: dict[str, Any] = {}
        if branches is not None:
            configs["branches"] = branches
        configs["types"] = ["completed"]
        configs["workflows"] = workflows
        return {"workflow_run": configs}

    def strategy_matrix_os_and_python_version(
        self,
        os: list[str] | None = None,
        python_versions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a strategy with OS and Python version matrix.

        Args:
            os: Runner labels to test against. Defaults to Ubuntu, Windows,
                and macOS latest (`ubuntu-latest`, `windows-latest`,
                `macos-latest`).
            python_versions: Python version strings to test against. Defaults
                to all versions returned by
                `PyprojectConfigFile.supported_python_versions()`.

        Returns:
            Strategy configuration containing the combined OS and Python
            version matrix.
        """
        return self.strategy_matrix(
            matrix={
                **self.matrix_os(os=os),
                **self.matrix_python_version(python_versions=python_versions),
            },
        )

    def strategy_matrix_python_version(
        self,
        python_versions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a strategy with Python version matrix.

        Args:
            python_versions: Python version strings to test against. Defaults
                to all versions returned by
                `PyprojectConfigFile.supported_python_versions()`.

        Returns:
            Strategy configuration containing the Python version matrix.
        """
        return self.strategy_matrix(
            matrix=self.matrix_python_version(python_versions=python_versions),
        )

    def strategy_matrix_os(
        self,
        os: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a strategy with OS matrix.

        Args:
            os: Runner labels to test against. Defaults to Ubuntu, Windows,
                and macOS latest (`ubuntu-latest`, `windows-latest`,
                `macos-latest`).

        Returns:
            Strategy configuration containing the OS matrix.
        """
        return self.strategy_matrix(matrix=self.matrix_os(os=os))

    def strategy_matrix(
        self,
        *,
        matrix: dict[str, list[Any]],
    ) -> dict[str, Any]:
        """Create a matrix strategy configuration.

        Args:
            matrix: Matrix dimensions.

        Returns:
            Strategy configuration with matrix.
        """
        return self.strategy(strategy={"matrix": matrix})

    def strategy(
        self,
        *,
        strategy: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply defaults to a strategy configuration.

        Sets `fail-fast` to `True` if not already present in the
        strategy dict.

        Args:
            strategy: Strategy configuration to process.

        Returns:
            The strategy dict with `fail-fast` defaulting to `True`.
        """
        strategy["fail-fast"] = strategy.pop("fail-fast", True)
        return strategy

    def matrix_os(
        self,
        *,
        os: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a matrix with OS dimension.

        Args:
            os: Runner labels to include. Defaults to Ubuntu, Windows, and
                macOS latest (`ubuntu-latest`, `windows-latest`,
                `macos-latest`).

        Returns:
            Matrix dict with the `os` key populated.
        """
        if os is None:
            os = [self.UBUNTU_LATEST, self.WINDOWS_LATEST, self.MACOS_LATEST]
        return self.matrix({"os": os})

    def matrix_python_version(
        self,
        *,
        python_versions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a matrix with Python version dimension.

        Args:
            python_versions: Python version strings to include. Defaults to
                all versions returned by
                `PyprojectConfigFile.supported_python_versions()`.

        Returns:
            Matrix dict with the `python-version` key populated.
        """
        if python_versions is None:
            python_versions = [
                str(v) for v in PyprojectConfigFile.I.supported_python_versions()
            ]
        return self.matrix({"python-version": python_versions})

    def matrix(self, matrix: dict[str, list[Any]]) -> dict[str, Any]:
        """Return the matrix configuration.

        This method is an extension point. The base implementation returns the
        dict unchanged; subclasses can override it to apply transformations or
        add fixed dimensions to every matrix produced by this workflow.

        Args:
            matrix: Matrix dimensions dict to pass through.

        Returns:
            The matrix configuration, unchanged by default.
        """
        return matrix

    def steps_core_installed_setup(
        self,
        *,
        python_version: str | None = None,
        update_dependencies: bool = False,
    ) -> list[dict[str, Any]]:
        """Build setup steps that include dependency installation.

        Produces steps for repository checkout, Python environment setup,
        optional dependency upgrade, and a full `uv sync`.

        Args:
            python_version: Python version string. Defaults to the latest
                minor version supported by the project.
            update_dependencies: Whether to include a step that updates all
                dependencies to their latest allowed versions before installing.

        Returns:
            Ordered list of step configuration dicts.
        """
        return [
            *self.steps_core_setup(
                python_version=python_version,
            ),
            *((self.step_update_dependencies(),) if update_dependencies else ()),
            self.step_install_dependencies(),
        ]

    def steps_core_setup(
        self,
        python_version: str | None = None,
    ) -> list[dict[str, Any]]:
        """Build the base checkout and environment setup steps.

        Checks out the repository and installs the package manager (`uv`) with
        the specified Python version. The containing job must grant at least
        `contents: read` through `permission_contents()`.

        Args:
            python_version: Python version string for `uv`. Defaults to the
                latest minor version supported by the project.

        Returns:
            Ordered list of step configuration dicts.
        """
        if python_version is None:
            python_version = str(
                PyprojectConfigFile.I.latest_possible_python_version(level="minor"),
            )
        return [
            self.step_checkout_repository(),
            self.step_setup_package_manager(python_version=python_version),
        ]

    def step_checkout_repository(self) -> dict[str, Any]:
        """Build a step that checks out the repository.

        Uses `actions/checkout@main`, which authenticates with the automatic
        `GITHUB_TOKEN`. Credential persistence is disabled since no later
        step needs the checked-out git credentials. The containing job must
        grant at least `contents: read` through
        `permission_contents()`.

        Returns:
            Step using `actions/checkout@main`.
        """
        return self.step(
            self.step_checkout_repository,
            uses="actions/checkout@main",
            with_={"persist-credentials": False},
        )

    def step_setup_package_manager(
        self,
        *,
        python_version: str,
    ) -> dict[str, Any]:
        """Build a step that installs uv and pins the Python version.

        Uses `astral-sh/setup-uv` to install uv on the runner and configure
        it to use the given Python version. All subsequent `uv run` and
        `uv sync` commands will use this version.

        Args:
            python_version: Python version string to pin, e.g. `"3.13"`.

        Returns:
            Step using `astral-sh/setup-uv@main`.
        """
        return self.step(
            self.step_setup_package_manager,
            uses="astral-sh/setup-uv@main",
            with_={"python-version": python_version},
        )

    def step_update_dependencies(self) -> dict[str, Any]:
        """Build a step that upgrades all pinned dependencies.

        Runs `uv lock --upgrade` to update the lock file to the latest
        versions allowed by the version constraints in `pyproject.toml`.

        Returns:
            Step that runs `uv lock --upgrade`.
        """
        return self.step(
            self.step_update_dependencies,
            run=str(PackageManager.I.update_dependencies_args()),
        )

    def step_install_dependencies(self) -> dict[str, Any]:
        """Build a step that synchronizes the virtual environment.

        Runs `uv sync` to install all locked dependencies.

        Returns:
            Step that runs `uv sync`.
        """
        return self.step(
            self.step_install_dependencies,
            run=str(PackageManager.I.install_dependencies_args()),
        )

    def repo_token_var(self) -> str:
        """Return the raw secrets expression for `REPO_TOKEN`.

        Returns:
            The `"secrets.REPO_TOKEN"` expression string.
        """
        return self.secrets_var(RemoteVersionController.I.access_token_key())

    def github_token_var(self) -> str:
        """Return the raw secrets expression for `GITHUB_TOKEN`.

        Returns:
            The `"secrets.GITHUB_TOKEN"` expression string.
        """
        return self.secrets_var("GITHUB_TOKEN")

    def secrets_var(self, name: str) -> str:
        """Build the raw GitHub secrets expression for a secret name.

        Args:
            name: The secret's key name (e.g. `"REPO_TOKEN"`).

        Returns:
            Raw expression string `"secrets.<name>"` suitable for use
            inside `${{ ... }}` wrappers.
        """
        return f"secrets.{name}"

    def insert_repo_token(self) -> str:
        """Return the `${{ secrets.REPO_TOKEN }}` expression.

        Returns:
            GitHub Actions expression for the `REPO_TOKEN` secret.
        """
        return self.insert_expression(self.repo_token_var())

    def shell_insert_version(self) -> str:
        """Build a shell command substitution for the project version.

        Evaluates `uv version --short` at workflow execution time, yielding the
        PEP 440 version string without any prefix (e.g. `1.2.3`).

        Returns:
            Shell command substitution string, e.g. `"$(uv version --short)"`.
            This syntax only works in shell contexts, not in GitHub Actions
            expressions.
        """
        return self.shell_insert_expression(str(PackageManager.I.version_short_args()))

    def insert_github_token(self) -> str:
        """Return the `${{ secrets.GITHUB_TOKEN }}` expression.

        Returns:
            GitHub Actions expression for the automatic `GITHUB_TOKEN`
            secret.
        """
        return self.insert_expression(self.github_token_var())

    def insert_matrix_os(self) -> str:
        """Return the expression that resolves to the current matrix OS value.

        Returns:
            GitHub Actions expression for `matrix.os`.
        """
        return self.insert_expression("matrix.os")

    def insert_matrix_python_version(self) -> str:
        """Return the expression that resolves to the current matrix Python version.

        Returns:
            GitHub Actions expression for `matrix.python-version`.
        """
        return self.insert_expression("matrix.python-version")

    def insert_github_workflow(self) -> str:
        """Return the expression that resolves to the current workflow's name.

        Returns:
            GitHub Actions expression for `github.workflow`.
        """
        return self.insert_expression("github.workflow")

    def insert_github_ref(self) -> str:
        """Return the expression that resolves to the triggering ref.

        Returns:
            GitHub Actions expression for `github.ref`.
        """
        return self.insert_expression("github.ref")

    def insert_github_workflow_and_ref(self) -> str:
        """Return the workflow name and ref joined into one group key.

        Returns:
            The `insert_github_workflow()` and `insert_github_ref()`
            expressions joined by a hyphen.
        """
        return f"{self.insert_github_workflow()}-{self.insert_github_ref()}"

    def shell_insert_expression(self, var: str) -> str:
        """Wrap an expression in shell command substitution `$( ... )` syntax.

        Args:
            var: The raw expression to wrap (e.g. `"uv version --short"`).

        Returns:
            The expression surrounded by `$( )` delimiters, e.g.
            `"$(uv version --short)"`.
        """
        return f"$({var})"

    def insert_expression(self, var: str) -> str:
        """Wrap an expression in GitHub Actions `${{ ... }}` syntax.

        Args:
            var: The raw expression to wrap
                (e.g. `"secrets.REPO_TOKEN"`).

        Returns:
            The expression surrounded by `${{ }}` delimiters, e.g.
            `"${{ secrets.REPO_TOKEN }}"`.
        """
        return f"${{{{ {var} }}}}"

    def if_workflow_run_is_success_and_push_triggered(self) -> str:
        """Build a condition true for a successful, push-triggered workflow run.

        Returns:
            GitHub Actions condition, true when the triggering workflow run
            both succeeded and was itself triggered by a push event.
        """
        return self.combined_if_and(
            self.if_workflow_run_is_success(),
            self.if_workflow_run_is_push_triggered(),
        )

    def if_workflow_run_is_success(self) -> str:
        """Build a condition that is true when the triggering workflow run succeeded.

        Not wrapped in `${{ }}`: GitHub evaluates a job/step `if:` value as
        an expression automatically.

        Returns:
            Bare GitHub Actions condition checking
            `github.event.workflow_run.conclusion == 'success'`.
        """
        return "github.event.workflow_run.conclusion == 'success'"

    def if_workflow_run_is_push_triggered(self) -> str:
        """Build a condition that is true when the triggering run was a push event.

        Not wrapped in `${{ }}`: GitHub evaluates a job/step `if:` value as
        an expression automatically.

        Returns:
            Bare GitHub Actions condition checking
            `github.event.workflow_run.event == 'push'`.
        """
        return "github.event.workflow_run.event == 'push'"

    def combined_if_and(self, *conditions: str) -> str:
        """Combine bare GitHub Actions conditions with a logical AND.

        Returns:
            The combined condition, one input condition per line.
        """
        return self.combined_if(*conditions, operator="&&")

    def combined_if_or(self, *conditions: str) -> str:
        """Combine bare GitHub Actions conditions with a logical OR.

        Returns:
            The combined condition, one input condition per line.
        """
        return self.combined_if(*conditions, operator="||")

    def combined_if(self, *conditions: str, operator: str) -> str:
        """Combine bare GitHub Actions conditions with a logical operator.

        One condition per line: the embedded newlines make the YAML dumper
        render this as a literal block scalar automatically, so a long
        combined condition stays within a linter's line-length limit.
        GitHub evaluates a bare (without `${{ }}`) job/step `if:` value as
        an expression automatically, and only the bare form supports
        splitting a condition across multiple lines — a `${{ }}`-wrapped
        multi-line value is read as a literal string instead of being
        evaluated. If one condition is provided, it is returned unchanged.

        Args:
            *conditions: Bare condition expressions (no `${{ }}` wrapper).
            operator: Logical operator to join conditions with, e.g. `"&&"`
                or `"||"`.

        Returns:
            The combined condition, one input condition per line.
        """
        return f" {operator}\n".join(conditions)
