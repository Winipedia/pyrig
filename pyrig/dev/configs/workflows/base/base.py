"""Base class for GitHub Actions workflow configuration.

This module provides the Workflow base class that all workflow
configuration files inherit from. It includes utilities for
building jobs, steps, triggers, and matrix strategies.
"""

from abc import abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pyrig
from pyrig.dev.builders.base.base import Builder
from pyrig.dev.configs.base.base import YamlConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.utils.packages import get_src_package
from pyrig.src.modules.package import (
    DependencyGraph,
)
from pyrig.src.project.mgt import (
    PROJECT_MGT,
    PROJECT_MGT_RUN_SCRIPT,
    get_project_mgt_run_pyrig_cli_cmd_script,
)
from pyrig.src.string import (
    make_name_from_obj,
    split_on_uppercase,
)


class Workflow(YamlConfigFile):
    """Abstract base class for GitHub Actions workflow configuration.

    Provides a declarative API for building workflow YAML files with
    jobs, steps, triggers, and matrix strategies. Subclasses must
    implement get_jobs() to define the workflow's jobs.

    Attributes:
        UBUNTU_LATEST: Runner label for Ubuntu.
        WINDOWS_LATEST: Runner label for Windows.
        MACOS_LATEST: Runner label for macOS.
        ARTIFACTS_DIR_NAME: Directory name for build artifacts.
        ARTIFACTS_PATTERN: Glob pattern for artifact files.
    """

    UBUNTU_LATEST = "ubuntu-latest"
    WINDOWS_LATEST = "windows-latest"
    MACOS_LATEST = "macos-latest"

    ARTIFACTS_DIR_NAME = Builder.ARTIFACTS_DIR_NAME
    ARTIFACTS_PATTERN = f"{ARTIFACTS_DIR_NAME}/*"

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load and parse the workflow configuration file.

        Returns:
            The parsed workflow configuration as a dict.
        """
        content = super().load()
        if not isinstance(content, dict):
            msg = f"Expected dict, got {type(content)}"
            raise TypeError(msg)
        return content

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Build the complete workflow configuration.

        Returns:
            Dict with name, triggers, permissions, defaults, env, and jobs.
        """
        return {
            "name": cls.get_workflow_name(),
            "on": cls.get_workflow_triggers(),
            "permissions": cls.get_permissions(),
            "run-name": cls.get_run_name(),
            "defaults": cls.get_defaults(),
            "env": cls.get_global_env(),
            "jobs": cls.get_jobs(),
        }

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for workflow files.

        Returns:
            Path to .github/workflows directory.
        """
        return Path(".github/workflows")

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the workflow configuration is correct.

        Handles the special case where workflow files cannot be empty.
        If empty, writes a minimal valid workflow that never triggers.

        Returns:
            True if configuration matches expected state.
        """
        correct = super().is_correct()

        if cls.get_path().read_text(encoding="utf-8") == "":
            config = cls.get_configs()
            jobs = config["jobs"]
            for job in jobs.values():
                job["steps"] = [cls.step_opt_out_of_workflow()]
            cls.dump(config)

        config = cls.load()
        jobs = config["jobs"]
        opted_out = all(
            job["steps"] == [cls.step_opt_out_of_workflow()] for job in jobs.values()
        )

        return correct or opted_out

    # Overridable Workflow Parts
    # ----------------------------------------------------------------------------
    @classmethod
    @abstractmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs.

        Subclasses must implement this to define their jobs.

        Returns:
            Dict mapping job IDs to job configurations.
        """

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Get the workflow triggers.

        Override to customize when the workflow runs.
        Default is manual workflow_dispatch only.

        Returns:
            Dict of trigger configurations.
        """
        return cls.on_workflow_dispatch()

    @classmethod
    def get_permissions(cls) -> dict[str, Any]:
        """Get the workflow permissions.

        Override to request additional permissions.
        Default is no extra permissions.

        Returns:
            Dict of permission settings.
        """
        return {}

    @classmethod
    def get_defaults(cls) -> dict[str, Any]:
        """Get the workflow defaults.

        Override to customize default settings.
        Default uses bash shell.

        Returns:
            Dict of default settings.
        """
        return {"run": {"shell": "bash"}}

    @classmethod
    def get_global_env(cls) -> dict[str, Any]:
        """Get the global environment variables.

        Override to add environment variables.
        Default disables Python bytecode writing.

        Returns:
            Dict of environment variables.
        """
        return {"PYTHONDONTWRITEBYTECODE": 1, "UV_NO_SYNC": 1}

    # Workflow Conventions
    # ----------------------------------------------------------------------------
    @classmethod
    def get_workflow_name(cls) -> str:
        """Generate a human-readable workflow name from the class name.

        Returns:
            Class name split on uppercase letters and joined with spaces.
        """
        name = cls.__name__.removesuffix(Workflow.__name__)
        return " ".join(split_on_uppercase(name))

    @classmethod
    def get_run_name(cls) -> str:
        """Get the display name for workflow runs.

        Returns:
            The workflow name by default.
        """
        return cls.get_workflow_name()

    # Build Utilities
    # ----------------------------------------------------------------------------
    @classmethod
    def get_job(  # noqa: PLR0913
        cls,
        job_func: Callable[..., Any],
        needs: list[str] | None = None,
        strategy: dict[str, Any] | None = None,
        permissions: dict[str, Any] | None = None,
        runs_on: str = UBUNTU_LATEST,
        if_condition: str | None = None,
        steps: list[dict[str, Any]] | None = None,
        job: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a job configuration.

        Args:
            job_func: Function representing the job, used to generate the ID.
            needs: List of job IDs this job depends on.
            strategy: Matrix or other strategy configuration.
            permissions: Job-level permissions.
            runs_on: Runner label. Defaults to ubuntu-latest.
            if_condition: Conditional expression for job execution.
            steps: List of step configurations.
            job: Existing job dict to update.

        Returns:
            Dict mapping job ID to job configuration.
        """
        name = cls.make_id_from_func(job_func)
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

    @classmethod
    def make_name_from_func(cls, func: Callable[..., Any]) -> str:
        """Generate a human-readable name from a function.

        Args:
            func: Function to extract name from.

        Returns:
            Formatted name with prefix removed.
        """
        name = make_name_from_obj(func, split_on="_", join_on=" ", capitalize=True)
        prefix = split_on_uppercase(name)[0]
        return name.removeprefix(prefix).strip()

    @classmethod
    def make_id_from_func(cls, func: Callable[..., Any]) -> str:
        """Generate a job/step ID from a function name.

        Args:
            func: Function to extract ID from.

        Returns:
            Function name with prefix removed.
        """
        name = getattr(func, "__name__", "")
        if not name:
            msg = f"Cannot extract name from {func}"
            raise ValueError(msg)
        prefix = name.split("_")[0]
        return name.removeprefix(f"{prefix}_")

    # triggers
    @classmethod
    def on_workflow_dispatch(cls) -> dict[str, Any]:
        """Create a manual workflow dispatch trigger.

        Returns:
            Trigger configuration for manual runs.
        """
        return {"workflow_dispatch": {}}

    @classmethod
    def on_push(cls, branches: list[str] | None = None) -> dict[str, Any]:
        """Create a push trigger.

        Args:
            branches: Branches to trigger on. Defaults to ["main"].

        Returns:
            Trigger configuration for push events.
        """
        if branches is None:
            branches = ["main"]
        return {"push": {"branches": branches}}

    @classmethod
    def on_schedule(cls, cron: str) -> dict[str, Any]:
        """Create a scheduled trigger.

        Args:
            cron: Cron expression for the schedule.

        Returns:
            Trigger configuration for scheduled runs.
        """
        return {"schedule": [{"cron": cron}]}

    @classmethod
    def on_pull_request(cls, types: list[str] | None = None) -> dict[str, Any]:
        """Create a pull request trigger.

        Args:
            types: PR event types. Defaults to opened, synchronize, reopened.

        Returns:
            Trigger configuration for pull request events.
        """
        if types is None:
            types = ["opened", "synchronize", "reopened"]
        return {"pull_request": {"types": types}}

    @classmethod
    def on_workflow_run(
        cls, workflows: list[str] | None = None, branches: list[str] | None = None
    ) -> dict[str, Any]:
        """Create a workflow run trigger.

        Args:
            workflows: Workflow names to trigger on. Defaults to this workflow.
            branches: Branches to filter on.

        Returns:
            Trigger configuration for workflow completion events.
        """
        if workflows is None:
            workflows = [cls.get_workflow_name()]
        config: dict[str, Any] = {"workflows": workflows, "types": ["completed"]}
        if branches is not None:
            config["branches"] = branches
        return {"workflow_run": config}

    # permissions
    @classmethod
    def permission_content(cls, permission: str = "read") -> dict[str, Any]:
        """Create a contents permission configuration.

        Args:
            permission: Permission level (read, write, none).

        Returns:
            Dict with contents permission.
        """
        return {"contents": permission}

    # Steps
    @classmethod
    def get_step(  # noqa: PLR0913
        cls,
        step_func: Callable[..., Any],
        run: str | None = None,
        if_condition: str | None = None,
        uses: str | None = None,
        with_: dict[str, Any] | None = None,
        env: dict[str, Any] | None = None,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a step configuration.

        Args:
            step_func: Function representing the step, used to generate name/ID.
            run: Shell command to execute.
            if_condition: Conditional expression for step execution.
            uses: GitHub Action to use.
            with_: Input parameters for the action.
            env: Environment variables for the step.
            step: Existing step dict to update.

        Returns:
            Step configuration dict.
        """
        if step is None:
            step = {}
        # make name from setup function name if name is a function
        name = cls.make_name_from_func(step_func)
        id_ = cls.make_id_from_func(step_func)
        step_config: dict[str, Any] = {"name": name, "id": id_}
        if run is not None:
            step_config["run"] = run
        if if_condition is not None:
            step_config["if"] = if_condition
        if uses is not None:
            step_config["uses"] = uses
        if with_ is not None:
            step_config["with"] = with_
        if env is not None:
            step_config["env"] = env

        step_config.update(step)

        return step_config

    # Strategy
    @classmethod
    def strategy_matrix_os_and_python_version(
        cls,
        os: list[str] | None = None,
        python_version: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
        strategy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a strategy with OS and Python version matrix.

        Args:
            os: List of OS runners. Defaults to all major platforms.
            python_version: List of Python versions. Defaults to supported versions.
            matrix: Additional matrix dimensions.
            strategy: Additional strategy options.

        Returns:
            Strategy configuration with OS and Python matrix.
        """
        return cls.strategy_matrix(
            matrix=cls.matrix_os_and_python_version(
                os=os, python_version=python_version, matrix=matrix
            ),
            strategy=strategy,
        )

    @classmethod
    def strategy_matrix_python_version(
        cls,
        python_version: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
        strategy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a strategy with Python version matrix.

        Args:
            python_version: List of Python versions. Defaults to supported versions.
            matrix: Additional matrix dimensions.
            strategy: Additional strategy options.

        Returns:
            Strategy configuration with Python version matrix.
        """
        return cls.strategy_matrix(
            matrix=cls.matrix_python_version(
                python_version=python_version, matrix=matrix
            ),
            strategy=strategy,
        )

    @classmethod
    def strategy_matrix_os(
        cls,
        os: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
        strategy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a strategy with OS matrix.

        Args:
            os: List of OS runners. Defaults to all major platforms.
            matrix: Additional matrix dimensions.
            strategy: Additional strategy options.

        Returns:
            Strategy configuration with OS matrix.
        """
        return cls.strategy_matrix(
            matrix=cls.matrix_os(os=os, matrix=matrix), strategy=strategy
        )

    @classmethod
    def strategy_matrix(
        cls,
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
        return cls.get_strategy(strategy=strategy)

    @classmethod
    def get_strategy(
        cls,
        *,
        strategy: dict[str, Any],
    ) -> dict[str, Any]:
        """Finalize a strategy configuration.

        Args:
            strategy: Strategy configuration to finalize.

        Returns:
            Strategy with fail-fast defaulting to True.
        """
        strategy["fail-fast"] = strategy.pop("fail-fast", True)
        return strategy

    @classmethod
    def matrix_os_and_python_version(
        cls,
        os: list[str] | None = None,
        python_version: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a matrix with OS and Python version dimensions.

        Args:
            os: List of OS runners. Defaults to all major platforms.
            python_version: List of Python versions. Defaults to supported versions.
            matrix: Additional matrix dimensions.

        Returns:
            Matrix configuration with os and python-version.
        """
        if matrix is None:
            matrix = {}
        os_matrix = cls.matrix_os(os=os, matrix=matrix)["os"]
        python_version_matrix = cls.matrix_python_version(
            python_version=python_version, matrix=matrix
        )["python-version"]
        matrix["os"] = os_matrix
        matrix["python-version"] = python_version_matrix
        return cls.get_matrix(matrix=matrix)

    @classmethod
    def matrix_os(
        cls,
        *,
        os: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a matrix with OS dimension.

        Args:
            os: List of OS runners. Defaults to Ubuntu, Windows, macOS.
            matrix: Additional matrix dimensions.

        Returns:
            Matrix configuration with os.
        """
        if os is None:
            os = [cls.UBUNTU_LATEST, cls.WINDOWS_LATEST, cls.MACOS_LATEST]
        if matrix is None:
            matrix = {}
        matrix["os"] = os
        return cls.get_matrix(matrix=matrix)

    @classmethod
    def matrix_python_version(
        cls,
        *,
        python_version: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a matrix with Python version dimension.

        Args:
            python_version: List of Python versions. Defaults to supported versions.
            matrix: Additional matrix dimensions.

        Returns:
            Matrix configuration with python-version.
        """
        if python_version is None:
            python_version = [
                str(v) for v in PyprojectConfigFile.get_supported_python_versions()
            ]
        if matrix is None:
            matrix = {}
        matrix["python-version"] = python_version
        return cls.get_matrix(matrix=matrix)

    @classmethod
    def get_matrix(cls, matrix: dict[str, list[Any]]) -> dict[str, Any]:
        """Return the matrix configuration.

        Args:
            matrix: Matrix dimensions.

        Returns:
            The matrix configuration unchanged.
        """
        return matrix

    # Workflow Steps
    # ----------------------------------------------------------------------------
    # Combined Steps
    @classmethod
    def steps_core_setup(
        cls, python_version: str | None = None, *, repo_token: bool = False
    ) -> list[dict[str, Any]]:
        """Get the core setup steps for any workflow.

        Args:
            python_version: Python version to use. Defaults to latest supported.
            repo_token: Whether to use REPO_TOKEN for checkout.

        Returns:
            List with checkout and project management setup steps.
        """
        if python_version is None:
            python_version = str(
                PyprojectConfigFile.get_latest_possible_python_version(level="minor")
            )
        return [
            cls.step_checkout_repository(repo_token=repo_token),
            cls.step_setup_git(),
            cls.step_setup_project_mgt(python_version=python_version),
        ]

    @classmethod
    def steps_core_installed_setup(
        cls,
        *,
        no_dev: bool = False,
        python_version: str | None = None,
        repo_token: bool = False,
    ) -> list[dict[str, Any]]:
        """Get core setup steps with dependency installation.

        Args:
            python_version: Python version to use. Defaults to latest supported.
            repo_token: Whether to use REPO_TOKEN for checkout.
            no_dev: Whether to install dev dependencies.

        Returns:
            List with setup, install, and dependency update steps.
        """
        return [
            *cls.steps_core_setup(python_version=python_version, repo_token=repo_token),
            cls.step_patch_version(),
            cls.step_install_python_dependencies(no_dev=no_dev),
            cls.step_add_dependency_updates_to_git(),
        ]

    @classmethod
    def steps_core_matrix_setup(
        cls,
        *,
        no_dev: bool = False,
        python_version: str | None = None,
        repo_token: bool = False,
    ) -> list[dict[str, Any]]:
        """Get core setup steps for matrix jobs.

        Args:
            python_version: Python version to use. Defaults to matrix value.
            repo_token: Whether to use REPO_TOKEN for checkout.
            no_dev: Whether to install dev dependencies.

        Returns:
            List with full setup steps for matrix execution.
        """
        return [
            *cls.steps_core_installed_setup(
                python_version=python_version,
                repo_token=repo_token,
                no_dev=no_dev,
            ),
        ]

    @classmethod
    def steps_configure_keyring_if_needed(cls) -> list[dict[str, Any]]:
        """Get keyring configuration steps if keyring is a dependency.

        Returns:
            List with keyring setup step if needed, empty otherwise.
        """
        steps: list[dict[str, Any]] = []
        if "keyring" in DependencyGraph.get_all_dependencies():
            steps.append(cls.step_setup_keyring())
        return steps

    # Single Step
    @classmethod
    def step_opt_out_of_workflow(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that opts out of the workflow.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that echoes an opt-out message.
        """
        return cls.get_step(
            step_func=cls.step_opt_out_of_workflow,
            run=f"echo 'Opting out of {cls.get_workflow_name()} workflow.'",
            step=step,
        )

    @classmethod
    def step_aggregate_matrix_results(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that aggregates matrix job results.

        Args:
            step: Existing step dict to update.

        Returns:
            Step configuration for result aggregation.
        """
        return cls.get_step(
            step_func=cls.step_aggregate_matrix_results,
            run="echo 'Aggregating matrix results into one job.'",
            step=step,
        )

    @classmethod
    def step_no_builder_defined(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a placeholder step when no builders are defined.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that echoes a skip message.
        """
        return cls.get_step(
            step_func=cls.step_no_builder_defined,
            run="echo 'No non-abstract builders defined. Skipping build.'",
            step=step,
        )

    @classmethod
    def step_install_container_engine(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that installs the container engine.

        We use podman as the container engine.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that installs podman.
        """
        return cls.get_step(
            step_func=cls.step_install_container_engine,
            uses="redhat-actions/podman-install@main",
            with_={"github-token": cls.insert_github_token()},
            step=step,
        )

    @classmethod
    def step_build_container_image(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that builds the container image.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that builds the container image.
        """
        return cls.get_step(
            step_func=cls.step_build_container_image,
            run=f"podman build -t {PyprojectConfigFile.get_project_name()} .",
            step=step,
        )

    @classmethod
    def step_save_container_image(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that saves the container image to a file.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that saves the container image.
        """
        image_file = Path(f"{PyprojectConfigFile.get_project_name()}.tar")
        image_path = Path(cls.ARTIFACTS_DIR_NAME) / image_file
        return cls.get_step(
            step_func=cls.step_save_container_image,
            run=f"podman save -o {image_path.as_posix()} {image_file.stem}",
            step=step,
        )

    @classmethod
    def step_make_dist_folder(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that makes the dist folder.

        Creates only if it does not exist.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that makes the dist folder.
        """
        return cls.get_step(
            step_func=cls.step_make_dist_folder,
            run=f"mkdir -p {Builder.ARTIFACTS_DIR_NAME}",
            step=step,
        )

    @classmethod
    def step_run_tests(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that runs pytest.

        Args:
            step: Existing step dict to update.

        Returns:
            Step configuration for running tests.
        """
        if step is None:
            step = {}
        if PyprojectConfigFile.get_package_name() == pyrig.__name__:
            step.setdefault("env", {})["REPO_TOKEN"] = cls.insert_repo_token()
        run = f"{PROJECT_MGT_RUN_SCRIPT} pytest --log-cli-level=INFO --cov-report=xml"
        return cls.get_step(
            step_func=cls.step_run_tests,
            run=run,
            step=step,
        )

    @classmethod
    def step_upload_coverage_report(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that uploads the coverage report.

        If the repository is private, the workflow will fail and
        a Codecov token has to be added to the repository secrets.
        You need an account on Codecov for this.
        This is why we fail_ci_if_error is not set to true.
        This is an optional service and should not break the workflow.

        Args:
            step: Existing step dict to update.

        Returns:
            Step configuration for uploading coverage report.
        """
        return cls.get_step(
            step_func=cls.step_upload_coverage_report,
            uses="codecov/codecov-action@main",
            with_={
                "files": "coverage.xml",
                "token": cls.insert_codecov_token(),
            },
            step=step,
        )

    @classmethod
    def step_patch_version(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that bumps the patch version.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that increments version and stages pyproject.toml.
        """
        return cls.get_step(
            step_func=cls.step_patch_version,
            run=f"{PROJECT_MGT} version --bump patch && git add pyproject.toml",
            step=step,
        )

    @classmethod
    def step_add_dependency_updates_to_git(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that stages dependency file changes.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that stages pyproject.toml and uv.lock.
        """
        return cls.get_step(
            step_func=cls.step_add_dependency_updates_to_git,
            run=f"git add pyproject.toml {PROJECT_MGT}.lock",
            step=step,
        )

    @classmethod
    def step_checkout_repository(
        cls,
        *,
        step: dict[str, Any] | None = None,
        fetch_depth: int | None = None,
        repo_token: bool = False,
    ) -> dict[str, Any]:
        """Create a step that checks out the repository.

        Args:
            step: Existing step dict to update.
            fetch_depth: Git fetch depth. None for full history.
            repo_token: Whether to use REPO_TOKEN for authentication.

        Returns:
            Step using actions/checkout.
        """
        if step is None:
            step = {}
        if fetch_depth is not None:
            step.setdefault("with", {})["fetch-depth"] = fetch_depth
        if repo_token:
            step.setdefault("with", {})["token"] = cls.insert_repo_token()
        return cls.get_step(
            step_func=cls.step_checkout_repository,
            uses="actions/checkout@main",
            step=step,
        )

    @classmethod
    def step_setup_git(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that configures git user for commits.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that sets git user.email and user.name.
        """
        return cls.get_step(
            step_func=cls.step_setup_git,
            run='git config --global user.email "github-actions[bot]@users.noreply.github.com" && git config --global user.name "github-actions[bot]"',  # noqa: E501
            step=step,
        )

    @classmethod
    def step_setup_python(
        cls,
        *,
        step: dict[str, Any] | None = None,
        python_version: str | None = None,
    ) -> dict[str, Any]:
        """Create a step that sets up Python.

        Args:
            step: Existing step dict to update.
            python_version: Python version to install. Defaults to latest.

        Returns:
            Step using actions/setup-python.
        """
        if step is None:
            step = {}
        if python_version is None:
            python_version = str(
                PyprojectConfigFile.get_latest_possible_python_version(level="minor")
            )

        step.setdefault("with", {})["python-version"] = python_version
        return cls.get_step(
            step_func=cls.step_setup_python,
            uses="actions/setup-python@main",
            step=step,
        )

    @classmethod
    def step_setup_project_mgt(
        cls,
        *,
        python_version: str | None = None,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that sets up the project management tool (uv).

        Args:
            python_version: Python version to configure.
            step: Existing step dict to update.

        Returns:
            Step using astral-sh/setup-uv.
        """
        return cls.get_step(
            step_func=cls.step_setup_project_mgt,
            uses="astral-sh/setup-uv@main",
            with_={"python-version": python_version},
            step=step,
        )

    @classmethod
    def step_build_wheel(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that builds the Python wheel.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs uv build.
        """
        return cls.get_step(
            step_func=cls.step_build_wheel,
            run=f"{PROJECT_MGT} build",
            step=step,
        )

    @classmethod
    def step_publish_to_pypi(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that publishes the package to PyPI.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs uv publish with PYPI_TOKEN.
        """
        return cls.get_step(
            step_func=cls.step_publish_to_pypi,
            run=f"{PROJECT_MGT} publish --token {cls.insert_pypi_token()}",
            step=step,
        )

    @classmethod
    def step_install_python_dependencies(
        cls,
        *,
        no_dev: bool = False,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that installs Python dependencies.

        Args:
            step: Existing step dict to update.
            no_dev: Whether to install dev dependencies.

        Returns:
            Step that runs uv sync.
        """
        upgrade = f"{PROJECT_MGT} lock --upgrade"
        install = f"{PROJECT_MGT} sync"
        if no_dev:
            install += " --no-group dev"
        run = f"{upgrade} && {install}"

        return cls.get_step(
            step_func=cls.step_install_python_dependencies,
            run=run,
            step=step,
        )

    @classmethod
    def step_setup_keyring(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that configures keyring for CI.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that sets up PlaintextKeyring for CI environments.
        """
        return cls.get_step(
            step_func=cls.step_setup_keyring,
            run=f'{PROJECT_MGT_RUN_SCRIPT} python -c "import keyring; from keyrings.alt.file import PlaintextKeyring; keyring.set_keyring(PlaintextKeyring());"',  # noqa: E501
            step=step,
        )

    @classmethod
    def step_protect_repository(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that applies repository protection rules.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs the pyrig protect-repo command.
        """
        from pyrig.dev.cli.subcommands import protect_repo  # noqa: PLC0415

        return cls.get_step(
            step_func=cls.step_protect_repository,
            run=get_project_mgt_run_pyrig_cli_cmd_script(protect_repo),
            env={"REPO_TOKEN": cls.insert_repo_token()},
            step=step,
        )

    @classmethod
    def step_run_pre_commit_hooks(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that runs pre-commit hooks.

        Ensures code quality checks pass before commits. Also useful
        for ensuring git stash pop doesn't fail when there are no changes.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs pre-commit on all files.
        """
        return cls.get_step(
            step_func=cls.step_run_pre_commit_hooks,
            run=f"{PROJECT_MGT_RUN_SCRIPT} pre-commit run --all-files",
            step=step,
        )

    @classmethod
    def step_commit_added_changes(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that commits staged changes.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that commits with [skip ci] prefix.
        """
        return cls.get_step(
            step_func=cls.step_commit_added_changes,
            run="git commit --no-verify -m '[skip ci] CI/CD: Committing possible added changes (e.g.: pyproject.toml)'",  # noqa: E501
            step=step,
        )

    @classmethod
    def step_push_commits(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that pushes commits to the remote.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs git push.
        """
        return cls.get_step(
            step_func=cls.step_push_commits,
            run="git push",
            step=step,
        )

    @classmethod
    def step_create_and_push_tag(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that creates and pushes a version tag.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that creates a git tag and pushes it.
        """
        return cls.get_step(
            step_func=cls.step_create_and_push_tag,
            run=f"git tag {cls.insert_version()} && git push origin {cls.insert_version()}",  # noqa: E501
            step=step,
        )

    @classmethod
    def step_create_folder(
        cls,
        *,
        folder: str,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that creates a directory.

        Args:
            folder: Directory name to create.
            step: Existing step dict to update.

        Returns:
            Step that runs mkdir (cross-platform).
        """
        # should work on all OSs
        return cls.get_step(
            step_func=cls.step_create_folder,
            run=f"mkdir {folder}",
            step=step,
        )

    @classmethod
    def step_create_artifacts_folder(
        cls,
        *,
        folder: str = Builder.ARTIFACTS_DIR_NAME,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that creates the artifacts directory.

        Args:
            folder: Directory name. Defaults to ARTIFACTS_DIR_NAME.
            step: Existing step dict to update.

        Returns:
            Step that creates the artifacts folder.
        """
        return cls.step_create_folder(folder=folder, step=step)

    @classmethod
    def step_upload_artifacts(
        cls,
        *,
        name: str | None = None,
        path: str | Path = ARTIFACTS_DIR_NAME,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that uploads build artifacts.

        Args:
            name: Artifact name. Defaults to package-os format.
            path: Path to upload. Defaults to artifacts directory.
            step: Existing step dict to update.

        Returns:
            Step using actions/upload-artifact.
        """
        if name is None:
            name = cls.insert_artifact_name()
        return cls.get_step(
            step_func=cls.step_upload_artifacts,
            uses="actions/upload-artifact@main",
            with_={"name": name, "path": str(path)},
            step=step,
        )

    @classmethod
    def step_build_artifacts(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that builds project artifacts.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs the pyrig build command.
        """
        from pyrig.dev.cli.subcommands import build  # noqa: PLC0415

        return cls.get_step(
            step_func=cls.step_build_artifacts,
            run=get_project_mgt_run_pyrig_cli_cmd_script(build),
            step=step,
        )

    @classmethod
    def step_download_artifacts(
        cls,
        *,
        name: str | None = None,
        path: str | Path = ARTIFACTS_DIR_NAME,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that downloads build artifacts.

        Args:
            name: Artifact name to download. None downloads all.
            path: Path to download to. Defaults to artifacts directory.
            step: Existing step dict to update.

        Returns:
            Step using actions/download-artifact.
        """
        # omit name downloads all by default
        with_: dict[str, Any] = {"path": str(path)}
        if name is not None:
            with_["name"] = name
        with_["merge-multiple"] = "true"
        return cls.get_step(
            step_func=cls.step_download_artifacts,
            uses="actions/download-artifact@main",
            with_=with_,
            step=step,
        )

    @classmethod
    def step_download_artifacts_from_workflow_run(
        cls,
        *,
        name: str | None = None,
        path: str | Path = ARTIFACTS_DIR_NAME,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that downloads artifacts from triggering workflow run.

        Uses the github.event.workflow_run.id to download artifacts from
        the workflow that triggered this workflow (via workflow_run event).

        Args:
            name: Artifact name to download. None downloads all.
            path: Path to download to. Defaults to artifacts directory.
            step: Existing step dict to update.

        Returns:
            Step using actions/download-artifact with run-id parameter.
        """
        with_: dict[str, Any] = {
            "path": str(path),
            "run-id": cls.insert_workflow_run_id(),
            "github-token": cls.insert_github_token(),
        }
        if name is not None:
            with_["name"] = name
        with_["merge-multiple"] = "true"
        return cls.get_step(
            step_func=cls.step_download_artifacts_from_workflow_run,
            uses="actions/download-artifact@main",
            with_=with_,
            step=step,
        )

    @classmethod
    def step_build_changelog(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that generates a changelog.

        Args:
            step: Existing step dict to update.

        Returns:
            Step using release-changelog-builder-action.
        """
        return cls.get_step(
            step_func=cls.step_build_changelog,
            uses="mikepenz/release-changelog-builder-action@develop",
            with_={"token": cls.insert_github_token()},
            step=step,
        )

    @classmethod
    def step_extract_version(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that extracts the version to GITHUB_OUTPUT.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that outputs the version for later steps.
        """
        return cls.get_step(
            step_func=cls.step_extract_version,
            run=f'echo "version={cls.insert_version()}" >> $GITHUB_OUTPUT',
            step=step,
        )

    @classmethod
    def step_create_release(
        cls,
        *,
        step: dict[str, Any] | None = None,
        artifacts_pattern: str = ARTIFACTS_PATTERN,
    ) -> dict[str, Any]:
        """Create a step that creates a GitHub release.

        Args:
            step: Existing step dict to update.
            artifacts_pattern: Glob pattern for release artifacts.

        Returns:
            Step using ncipollo/release-action.
        """
        version = cls.insert_version_from_extract_version_step()
        return cls.get_step(
            step_func=cls.step_create_release,
            uses="ncipollo/release-action@main",
            with_={
                "tag": version,
                "name": f"{cls.insert_repository_name()} {version}",
                "body": cls.insert_changelog(),
                "artifacts": artifacts_pattern,
            },
            step=step,
        )

    # Insertions
    # ----------------------------------------------------------------------------
    @classmethod
    def insert_repo_token(cls) -> str:
        """Get the GitHub expression for REPO_TOKEN secret.

        Returns:
            GitHub Actions expression for secrets.REPO_TOKEN.
        """
        return "${{ secrets.REPO_TOKEN }}"

    @classmethod
    def insert_pypi_token(cls) -> str:
        """Get the GitHub expression for PYPI_TOKEN secret.

        Returns:
            GitHub Actions expression for secrets.PYPI_TOKEN.
        """
        return "${{ secrets.PYPI_TOKEN }}"

    @classmethod
    def insert_version(cls) -> str:
        """Get a shell expression for the current version.

        Returns:
            Shell command that outputs the version with v prefix.
        """
        return f"v$({PROJECT_MGT} version --short)"

    @classmethod
    def insert_version_from_extract_version_step(cls) -> str:
        """Get the GitHub expression for version from extract step.

        Returns:
            GitHub Actions expression referencing the extract_version output.
        """
        # make dynamic with cls.make_id_from_func(cls.step_extract_version)
        return (
            "${{ "
            f"steps.{cls.make_id_from_func(cls.step_extract_version)}.outputs.version"
            " }}"
        )

    @classmethod
    def insert_changelog(cls) -> str:
        """Get the GitHub expression for changelog from build step.

        Returns:
            GitHub Actions expression referencing the build_changelog output.
        """
        return (
            "${{ "
            f"steps.{cls.make_id_from_func(cls.step_build_changelog)}.outputs.changelog"
            " }}"
        )

    @classmethod
    def insert_github_token(cls) -> str:
        """Get the GitHub expression for GITHUB_TOKEN.

        Returns:
            GitHub Actions expression for secrets.GITHUB_TOKEN.
        """
        return "${{ secrets.GITHUB_TOKEN }}"

    @classmethod
    def insert_codecov_token(cls) -> str:
        """Get the GitHub expression for CODECOV_TOKEN.

        Returns:
            GitHub Actions expression for secrets.CODECOV_TOKEN.
        """
        return "${{ secrets.CODECOV_TOKEN }}"

    @classmethod
    def insert_repository_name(cls) -> str:
        """Get the GitHub expression for repository name.

        Returns:
            GitHub Actions expression for the repository name.
        """
        return "${{ github.event.repository.name }}"

    @classmethod
    def insert_ref_name(cls) -> str:
        """Get the GitHub expression for the ref name.

        Returns:
            GitHub Actions expression for github.ref_name.
        """
        return "${{ github.ref_name }}"

    @classmethod
    def insert_repository_owner(cls) -> str:
        """Get the GitHub expression for repository owner.

        Returns:
            GitHub Actions expression for github.repository_owner.
        """
        return "${{ github.repository_owner }}"

    @classmethod
    def insert_workflow_run_id(cls) -> str:
        """Get the GitHub expression for triggering workflow run ID.

        Used when downloading artifacts from the workflow that triggered
        this workflow via workflow_run event.

        Returns:
            GitHub Actions expression for github.event.workflow_run.id.
        """
        return "${{ github.event.workflow_run.id }}"

    @classmethod
    def insert_os(cls) -> str:
        """Get the GitHub expression for runner OS.

        Returns:
            GitHub Actions expression for runner.os.
        """
        return "${{ runner.os }}"

    @classmethod
    def insert_matrix_os(cls) -> str:
        """Get the GitHub expression for matrix OS value.

        Returns:
            GitHub Actions expression for matrix.os.
        """
        return "${{ matrix.os }}"

    @classmethod
    def insert_matrix_python_version(cls) -> str:
        """Get the GitHub expression for matrix Python version.

        Returns:
            GitHub Actions expression for matrix.python-version.
        """
        return "${{ matrix.python-version }}"

    @classmethod
    def insert_artifact_name(cls) -> str:
        """Generate an artifact name based on package and OS.

        Returns:
            Artifact name in format: package-os.
        """
        return f"{get_src_package().__name__}-{cls.insert_os()}"

    # ifs
    # ----------------------------------------------------------------------------
    @classmethod
    def combined_if(cls, *conditions: str) -> str:
        """Combine multiple conditions with logical AND.

        Args:
            *conditions: Individual condition expressions.

        Returns:
            Combined condition expression.
        """
        bare_conditions = [
            condition.strip().removeprefix("${{").removesuffix("}}").strip()
            for condition in conditions
        ]
        return cls.if_condition(" && ".join(bare_conditions))

    @classmethod
    def if_condition(cls, condition: str) -> str:
        """Wrap a condition in GitHub Actions expression syntax.

        Args:
            condition: Condition expression to wrap.

        Returns:
            GitHub Actions expression for the condition.
        """
        return f"${{{{ {condition} }}}}"

    @classmethod
    def if_matrix_is_not_os(cls, os: str) -> str:
        """Create a condition for not matching a specific OS.

        Args:
            os: OS runner label to not match.

        Returns:
            Condition expression for matrix.os comparison.
        """
        return cls.if_condition(f"matrix.os != '{os}'")

    @classmethod
    def if_workflow_run_is_success(cls) -> str:
        """Create a condition for successful workflow run.

        Returns:
            GitHub Actions expression checking workflow_run conclusion.
        """
        return cls.if_condition("github.event.workflow_run.conclusion == 'success'")
