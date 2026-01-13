"""Base class for GitHub Actions workflow configuration.

This module provides the Workflow base class that all workflow configuration
files inherit from. It includes comprehensive utilities for building GitHub
Actions workflows programmatically.

The Workflow class provides:
    - **Job Builders**: Methods for creating common CI/CD jobs (test, build,
      release, publish)
    - **Step Builders**: Reusable step templates (checkout, setup Python, cache,
      run commands)
    - **Trigger Builders**: Methods for defining workflow triggers (push, PR,
      schedule, workflow_run)
    - **Matrix Strategies**: OS and Python version matrix configuration
    - **Artifact Management**: Upload/download artifact utilities
    - **Environment Setup**: Automatic uv, Python, and dependency installation

Key Features:
    - Type-safe workflow configuration using Python dicts
    - Reusable templates for common CI/CD patterns
    - Integration with pyrig's management tools (Pyrigger, PackageManager, etc.)
    - Support for multi-OS testing (Ubuntu, macOS, Windows)
    - Support for multi-Python version testing
    - Automatic caching for dependencies and build artifacts

See Also:
    pyrig.dev.configs.workflows
        Concrete workflow implementations
    GitHub Actions: https://docs.github.com/en/actions
"""

from abc import abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pyrig.dev.builders.base.base import BuilderConfigFile
from pyrig.dev.cli.subcommands import build, protect_repo
from pyrig.dev.configs.base.yaml import YamlConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.management.container_engine import (
    ContainerEngine,
)
from pyrig.dev.management.dependency_auditor import DependencyAuditor
from pyrig.dev.management.docs_builder import DocsBuilder
from pyrig.dev.management.package_manager import PackageManager
from pyrig.dev.management.pre_committer import PreCommitter
from pyrig.dev.management.project_tester import ProjectTester
from pyrig.dev.management.pyrigger import Pyrigger
from pyrig.dev.management.version_controller import VersionController
from pyrig.dev.utils.packages import src_pkg_is_pyrig
from pyrig.src.string_ import (
    make_name_from_obj,
    split_on_uppercase,
)


class Workflow(YamlConfigFile):
    """Abstract base class for GitHub Actions workflow configuration.

    Provides a declarative API for building GitHub Actions workflow YAML files
    programmatically. Subclasses define specific workflows by implementing
    get_jobs() and optionally overriding trigger/permission methods.

    The class provides extensive utilities for:
        - Creating jobs with matrix strategies
        - Building reusable step sequences
        - Defining workflow triggers (push, PR, schedule, workflow_run)
        - Managing artifacts and caching
        - Setting up Python environments with uv
        - Running pyrig management commands

    Subclasses should:
        1. Implement get_jobs() to define workflow jobs
        2. Override get_workflow_triggers() to customize triggers
        3. Override get_permissions() if special permissions needed

    Attributes:
        UBUNTU_LATEST (str): Runner label for Ubuntu ("ubuntu-latest")
        WINDOWS_LATEST (str): Runner label for Windows ("windows-latest")
        MACOS_LATEST (str): Runner label for macOS ("macos-latest")
        ARTIFACTS_DIR_NAME (str): Directory name for build artifacts
        ARTIFACTS_PATTERN (str): Glob pattern for artifact files

    Examples:
        Create a custom workflow::

            from pyrig.dev.configs.base.workflow import Workflow

            class MyWorkflow(Workflow):
                @classmethod
                def get_jobs(cls) -> dict[str, Any]:
                    return {
                        "test": cls.job_test(),
                        "build": cls.job_build_artifacts(),
                    }

                @classmethod
                def get_workflow_triggers(cls) -> dict[str, Any]:
                    triggers = super().get_workflow_triggers()
                    triggers.update(cls.on_push())
                    return triggers

    See Also:
        pyrig.dev.configs.workflows.health_check.HealthCheckWorkflow
            Example concrete workflow implementation
        pyrig.dev.configs.base.yaml.YamlConfigFile
            Base class for YAML configuration files
    """

    UBUNTU_LATEST = "ubuntu-latest"
    WINDOWS_LATEST = "windows-latest"
    MACOS_LATEST = "macos-latest"

    ARTIFACTS_DIR_NAME = BuilderConfigFile.ARTIFACTS_DIR_NAME
    ARTIFACTS_PATTERN = f"{ARTIFACTS_DIR_NAME}/*"

    @classmethod
    def _get_configs(cls) -> dict[str, Any]:
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
        outputs: dict[str, str] | None = None,
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
            outputs: Job outputs mapping output names to step output references.
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
        if outputs is not None:
            job_config["outputs"] = outputs
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
            branches = [VersionController.L.get_default_branch()]
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
                str(v) for v in PyprojectConfigFile.L.get_supported_python_versions()
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
                PyprojectConfigFile.L.get_latest_possible_python_version(level="minor")
            )
        return [
            cls.step_checkout_repository(repo_token=repo_token),
            cls.step_setup_version_control(),
            cls.step_setup_package_manager(python_version=python_version),
        ]

    @classmethod
    def steps_core_installed_setup(
        cls,
        *,
        no_dev: bool = False,
        python_version: str | None = None,
        repo_token: bool = False,
    ) -> list[dict[str, Any]]:
        """Get core setup steps with dependency update and installation.

        Args:
            python_version: Python version to use. Defaults to latest supported.
            repo_token: Whether to use REPO_TOKEN for checkout.
            no_dev: Whether to install dev dependencies.

        Returns:
            List with setup, dependency update, and dependency installation steps.
        """
        return [
            *cls.steps_core_setup(python_version=python_version, repo_token=repo_token),
            cls.step_update_dependencies(),
            cls.step_install_dependencies(no_dev=no_dev),
            cls.step_add_dependency_updates_to_version_control(),
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
            no_dev: Whether to skip dev dependencies.
            python_version: Python version to use. If None (default),
                steps_core_installed_setup will use latest supported version.
            repo_token: Whether to use REPO_TOKEN for checkout.

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
    def step_aggregate_jobs(
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
            step_func=cls.step_aggregate_jobs,
            run="echo 'Aggregating jobs into one job.'",
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
            run=str(
                ContainerEngine.L.get_build_args(
                    project_name=PyprojectConfigFile.L.get_project_name()
                )
            ),
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
        image_file = Path(f"{PyprojectConfigFile.L.get_project_name()}.tar")
        image_path = Path(cls.ARTIFACTS_DIR_NAME) / image_file
        return cls.get_step(
            step_func=cls.step_save_container_image,
            run=str(
                ContainerEngine.L.get_save_args(
                    image_file=image_file,
                    image_path=image_path,
                )
            ),
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
            run=f"mkdir -p {cls.ARTIFACTS_DIR_NAME}",
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
        if src_pkg_is_pyrig():
            step.setdefault("env", {})["REPO_TOKEN"] = cls.insert_repo_token()
        run = str(
            PackageManager.L.get_run_args(*ProjectTester.L.get_run_tests_in_ci_args())
        )
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

        Requires a Codecov account (log in at codecov.io with GitHub).

        For private repos: CODECOV_TOKEN is required.
        For public repos: CODECOV_TOKEN is recommended, or enable tokenless
        upload in Codecov settings (Settings → General).

        If CODECOV_TOKEN is not defined, fail_ci_if_error is set to false,
        preventing the step from failing CI on upload errors.

        Args:
            step: Existing step dict to update.

        Returns:
            Step configuration for uploading coverage report.
        """
        #  make fail_ci_if_error true if token exists and false if it doesn't
        fail_ci_if_error = cls.insert_var(
            "${{ secrets.CODECOV_TOKEN && 'true' || 'false' }}"
        )
        return cls.get_step(
            step_func=cls.step_upload_coverage_report,
            uses="codecov/codecov-action@main",
            with_={
                "files": "coverage.xml",
                "token": cls.insert_codecov_token(),
                "fail_ci_if_error": fail_ci_if_error,
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
            run=str(PackageManager.L.get_patch_version_args()),
            step=step,
        )

    @classmethod
    def step_add_version_bump_to_version_control(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that stages the version bump commit.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that stages pyproject.toml.
        """
        return cls.get_step(
            step_func=cls.step_add_version_bump_to_version_control,
            run=str(VersionController.L.get_add_pyproject_toml_and_lock_file_args()),
            step=step,
        )

    @classmethod
    def step_add_dependency_updates_to_version_control(
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
            step_func=cls.step_add_dependency_updates_to_version_control,
            run=str(VersionController.L.get_add_pyproject_toml_and_lock_file_args()),
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
    def step_setup_version_control(
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
            step_func=cls.step_setup_version_control,
            run=str(
                VersionController.L.get_config_global_user_email_args(
                    email='"github-actions[bot]@users.noreply.github.com"',
                ),
            )
            + " && "
            + str(
                VersionController.L.get_config_global_user_name_args(
                    name='"github-actions[bot]"'
                )
            ),
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
                PyprojectConfigFile.L.get_latest_possible_python_version(level="minor")
            )

        step.setdefault("with", {})["python-version"] = python_version
        return cls.get_step(
            step_func=cls.step_setup_python,
            uses="actions/setup-python@main",
            step=step,
        )

    @classmethod
    def step_setup_package_manager(
        cls,
        *,
        python_version: str,
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
            step_func=cls.step_setup_package_manager,
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
            run=str(PackageManager.L.get_build_args()),
            step=step,
        )

    @classmethod
    def step_publish_to_pypi(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that publishes the package to PyPI.

        If PYPI_TOKEN is not defined then the step is skipped.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs uv publish with PYPI_TOKEN.
        """
        run = str(PackageManager.L.get_publish_args(token=cls.insert_pypi_token()))
        run_if = cls.run_if_condition(run, cls.insert_pypi_token())
        return cls.get_step(
            step_func=cls.step_publish_to_pypi,
            run=run_if,
            step=step,
        )

    @classmethod
    def step_build_documentation(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that builds the documentation.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs uv build-docs.
        """
        return cls.get_step(
            step_func=cls.step_build_documentation,
            run=str(PackageManager.L.get_run_args(*DocsBuilder.L.get_build_args())),
            step=step,
        )

    @classmethod
    def step_enable_pages(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that enables GitHub Pages.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that enables GitHub Pages.
        """
        return cls.get_step(
            step_func=cls.step_enable_pages,
            uses="actions/configure-pages@main",
            with_={"token": cls.insert_repo_token(), "enablement": "true"},
            step=step,
        )

    @classmethod
    def step_upload_documentation(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that uploads the documentation to GitHub Pages.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that uploads the documentation to GitHub Pages.
        """
        return cls.get_step(
            step_func=cls.step_upload_documentation,
            uses="actions/upload-pages-artifact@main",
            with_={"path": "site"},
            step=step,
        )

    @classmethod
    def step_publish_documentation(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that publishes the documentation to GitHub Pages.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs uv publish-docs.
        """
        return cls.get_step(
            step_func=cls.step_publish_documentation,
            uses="actions/deploy-pages@main",
            step=step,
        )

    @classmethod
    def step_update_dependencies(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that updates the dependencies.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs uv lock --upgrade.
        """
        return cls.get_step(
            step_func=cls.step_update_dependencies,
            run=str(PackageManager.L.get_update_dependencies_args()),
            step=step,
        )

    @classmethod
    def step_install_dependencies(
        cls,
        *,
        no_dev: bool = False,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that installs Python dependencies.

        Args:
            no_dev: Whether to skip dev dependencies.
            step: Existing step dict to update.

        Returns:
            Step that runs uv sync.
        """
        install = str(PackageManager.L.get_install_dependencies_args())
        if no_dev:
            install += " --no-group dev"
        run = install

        return cls.get_step(
            step_func=cls.step_install_dependencies,
            run=run,
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
        return cls.get_step(
            step_func=cls.step_protect_repository,
            run=str(
                PackageManager.L.get_run_args(
                    *Pyrigger.L.get_cmd_args(cmd=protect_repo)
                )
            ),
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
            run=str(
                PackageManager.L.get_run_args(*PreCommitter.L.get_run_all_files_args())
            ),
            step=step,
        )

    @classmethod
    def step_run_dependency_audit(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that audits installed dependencies for known vulnerabilities.

        Runs pip-audit via uv (``uv run pip-audit``) so the audit uses the
        workflow's installed environment.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs pip-audit.
        """
        return cls.get_step(
            step_func=cls.step_run_dependency_audit,
            run=str(
                PackageManager.L.get_run_args(*DependencyAuditor.L.get_audit_args())
            ),
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
        msg = '"[skip ci] CI/CD: Committing possible changes (e.g.: pyproject.toml)"'
        return cls.get_step(
            step_func=cls.step_commit_added_changes,
            run=str(VersionController.L.get_commit_no_verify_args(msg=msg)),
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
            run=str(VersionController.L.get_push_args()),
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
            run=str(VersionController.L.get_tag_args(tag=cls.insert_version()))
            + " && "
            + str(
                VersionController.L.get_push_origin_tag_args(tag=cls.insert_version())
            ),
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
        folder: str = BuilderConfigFile.ARTIFACTS_DIR_NAME,
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
        return cls.get_step(
            step_func=cls.step_build_artifacts,
            run=str(PackageManager.L.get_run_args(*Pyrigger.L.get_cmd_args(cmd=build))),
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
    def insert_var(cls, var: str) -> str:
        """Wrap a variable in GitHub Actions expression syntax.

        Args:
            var: Variable expression to wrap.

        Returns:
            GitHub Actions expression for the variable.
        """
        # remove existing wrapping if it exists
        var = var.strip().removeprefix("${{").removesuffix("}}").strip()
        return f"${{{{ {var} }}}}"

    @classmethod
    def insert_repo_token(cls) -> str:
        """Get the GitHub expression for REPO_TOKEN secret.

        Returns:
            GitHub Actions expression for secrets.REPO_TOKEN.
        """
        return cls.insert_var("secrets.REPO_TOKEN")

    @classmethod
    def insert_pypi_token(cls) -> str:
        """Get the GitHub expression for PYPI_TOKEN secret.

        Returns:
            GitHub Actions expression for secrets.PYPI_TOKEN.
        """
        return cls.insert_var("secrets.PYPI_TOKEN")

    @classmethod
    def insert_version(cls) -> str:
        """Get a shell expression for the current version.

        Returns:
            Shell command that outputs the version with v prefix.
        """
        script = str(PackageManager.L.get_version_short_args())
        return f"v$({script})"

    @classmethod
    def insert_version_from_extract_version_step(cls) -> str:
        """Get the GitHub expression for version from extract step.

        Returns:
            GitHub Actions expression referencing the extract_version output.
        """
        # make dynamic with cls.make_id_from_func(cls.step_extract_version)
        return cls.insert_var(
            f"steps.{cls.make_id_from_func(cls.step_extract_version)}.outputs.version"
        )

    @classmethod
    def insert_changelog(cls) -> str:
        """Get the GitHub expression for changelog from build step.

        Returns:
            GitHub Actions expression referencing the build_changelog output.
        """
        return cls.insert_var(
            f"steps.{cls.make_id_from_func(cls.step_build_changelog)}.outputs.changelog"
        )

    @classmethod
    def insert_github_token(cls) -> str:
        """Get the GitHub expression for GITHUB_TOKEN.

        Returns:
            GitHub Actions expression for secrets.GITHUB_TOKEN.
        """
        return cls.insert_var("secrets.GITHUB_TOKEN")

    @classmethod
    def insert_codecov_token(cls) -> str:
        """Get the GitHub expression for CODECOV_TOKEN.

        Returns:
            GitHub Actions expression for secrets.CODECOV_TOKEN.
        """
        return cls.insert_var("secrets.CODECOV_TOKEN")

    @classmethod
    def insert_repository_name(cls) -> str:
        """Get the GitHub expression for repository name.

        Returns:
            GitHub Actions expression for the repository name.
        """
        return cls.insert_var("github.event.repository.name")

    @classmethod
    def insert_ref_name(cls) -> str:
        """Get the GitHub expression for the ref name.

        Returns:
            GitHub Actions expression for github.ref_name.
        """
        return cls.insert_var("github.ref_name")

    @classmethod
    def insert_repository_owner(cls) -> str:
        """Get the GitHub expression for repository owner.

        Returns:
            GitHub Actions expression for github.repository_owner.
        """
        return cls.insert_var("github.repository_owner")

    @classmethod
    def insert_workflow_run_id(cls) -> str:
        """Get the GitHub expression for triggering workflow run ID.

        Used when downloading artifacts from the workflow that triggered
        this workflow via workflow_run event.

        Returns:
            GitHub Actions expression for github.event.workflow_run.id.
        """
        return cls.insert_var("github.event.workflow_run.id")

    @classmethod
    def insert_os(cls) -> str:
        """Get the GitHub expression for runner OS.

        Returns:
            GitHub Actions expression for runner.os.
        """
        return cls.insert_var("runner.os")

    @classmethod
    def insert_matrix_os(cls) -> str:
        """Get the GitHub expression for matrix OS value.

        Returns:
            GitHub Actions expression for matrix.os.
        """
        return cls.insert_var("matrix.os")

    @classmethod
    def insert_matrix_python_version(cls) -> str:
        """Get the GitHub expression for matrix Python version.

        Returns:
            GitHub Actions expression for matrix.python-version.
        """
        return cls.insert_var("matrix.python-version")

    @classmethod
    def insert_artifact_name(cls) -> str:
        """Generate an artifact name based on package and OS.

        Returns:
            Artifact name in format: package-os.
        """
        return f"{PyprojectConfigFile.L.get_project_name()}-{cls.insert_os()}"

    # ifs
    # ----------------------------------------------------------------------------
    @classmethod
    def combined_if(cls, *conditions: str, operator: str) -> str:
        """Combine multiple conditions with a logical operator.

        Args:
            *conditions: Individual condition expressions.
            operator: Logical operator to combine conditions (e.g., "&&", "||").

        Returns:
            Combined condition expression wrapped in GitHub Actions syntax.
        """
        bare_conditions = [
            condition.strip().removeprefix("${{").removesuffix("}}").strip()
            for condition in conditions
        ]
        return cls.insert_var(f" {operator} ".join(bare_conditions))

    @classmethod
    def if_matrix_is_not_os(cls, os: str) -> str:
        """Create a condition for not matching a specific OS.

        Args:
            os: OS runner label to not match.

        Returns:
            Condition expression for matrix.os comparison.
        """
        return cls.insert_var(f"matrix.os != '{os}'")

    @classmethod
    def if_not_triggered_by_cron(cls) -> str:
        """Create a condition for not being triggered by cron.

        Returns:
            GitHub Actions expression checking event name.
        """
        return cls.insert_var("github.event_name != 'schedule'")

    @classmethod
    def if_workflow_run_is_success(cls) -> str:
        """Create a condition for successful workflow run.

        Returns:
            GitHub Actions expression checking workflow_run conclusion.
        """
        return cls.insert_var("github.event.workflow_run.conclusion == 'success'")

    @classmethod
    def if_workflow_run_is_not_cron_triggered(cls) -> str:
        """Create a condition for not being triggered by cron.

        Returns:
            GitHub Actions expression checking event name.
        """
        return cls.insert_var("github.event.workflow_run.event != 'schedule'")

    @classmethod
    def if_pypi_token_configured(cls) -> str:
        """Create a condition for PYPI_TOKEN being configured.

        Returns:
            GitHub Actions expression checking for PYPI_TOKEN.
        """
        return cls.insert_var("secrets.PYPI_TOKEN != ''")

    @classmethod
    def if_codecov_token_configured(cls) -> str:
        """Create a condition for CODECOV_TOKEN being configured.

        Returns:
            GitHub Actions expression checking for CODECOV_TOKEN.
        """
        return cls.insert_var("secrets.CODECOV_TOKEN != ''")

    # Runs
    # ----------------------------------------------------------------------------
    @classmethod
    def run_if_condition(cls, run: str, condition: str) -> str:
        """Returns a run command that only runs if condition is true.

        Args:
            run: Command to run.
            condition: Condition expression.

        Returns:
            GitHub Actions expression checking for condition.
        """
        condition_check = cls.insert_var(condition)
        # make a script that runs the command if the token is configured
        # and echos a message if it is not
        condition_as_str = (
            condition_check.strip().removeprefix("${{").removesuffix("}}").strip()
        )
        msg = f"Skipping step due to failed condition: {condition_as_str}."
        return f'if [ {condition_check} ]; then {run}; else echo "{msg}"; fi'
