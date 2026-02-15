"""Base class for GitHub Actions workflow configuration.

This module provides the WorkflowConfigFile base class that all workflow configuration
files inherit from. It includes comprehensive utilities for building GitHub
Actions workflows programmatically.

The WorkflowConfigFile class provides:
    - **Job Builders**: Methods for creating common CI/CD jobs (test, build,
      release, deploy)
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
    - Integration with pyrig's tools (Pyrigger, PackageManager, etc.)
    - Support for multi-OS testing (Ubuntu, macOS, Windows)
    - Support for multi-Python version testing
    - Automatic caching for dependencies and build artifacts

See Also:
    pyrig.rig.configs.workflows
        Concrete workflow implementations
    GitHub Actions: https://docs.github.com/en/actions
"""

from abc import abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pyrig.rig.builders.base.base import BuilderConfigFile
from pyrig.rig.cli.subcommands import build, protect_repo
from pyrig.rig.configs.base.yml import YmlConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.container_engine import (
    ContainerEngine,
)
from pyrig.rig.tools.dependency_auditor import DependencyAuditor
from pyrig.rig.tools.docs_builder import DocsBuilder
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pre_committer import PreCommitter
from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.packages import src_package_is_pyrig
from pyrig.src.string_ import (
    make_name_from_obj,
    split_on_uppercase,
)


class WorkflowConfigFile(YmlConfigFile):
    """Abstract base class for GitHub Actions workflow configuration.

    Provides a declarative API for building GitHub Actions workflow YAML files
    programmatically. Subclasses define specific workflows by implementing
    jobs() and optionally overriding trigger/permission methods.

    The class provides extensive utilities for:
        - Creating jobs with matrix strategies
        - Building reusable step sequences
        - Defining workflow triggers (push, PR, schedule, workflow_run)
        - Managing artifacts and caching
        - Setting up Python environments with uv
        - Running pyrig commands

    Subclasses should:
        1. Implement jobs() to define workflow jobs
        2. Override workflow_triggers() to customize triggers
        3. Override permissions() if special permissions needed

    Attributes:
        UBUNTU_LATEST (str): Runner label for Ubuntu ("ubuntu-latest")
        WINDOWS_LATEST (str): Runner label for Windows ("windows-latest")
        MACOS_LATEST (str): Runner label for macOS ("macos-latest")

    Example:
        >>> from pyrig.rig.configs.base.workflow import WorkflowConfigFile
        >>>
        >>> class MyWorkflowConfigFile(WorkflowConfigFile):
        ...
        ...     def jobs(self) -> dict[str, Any]:
        ...         return self.job(
        ...             job_func=self.jobs,
        ...             steps=[
        ...                 *self.steps_core_installed_setup(),
        ...                 self.step_run_tests(),
        ...             ],
        ...         )
        ...
        ...
        ...     def workflow_triggers(self) -> dict[str, Any]:
        ...         triggers = super().workflow_triggers()
        ...         triggers.update(self.on_push())
        ...         return triggers

    See Also:
        pyrig.rig.configs.workflows.health_check.HealthCheckWorkflowConfigFile
            Example concrete workflow implementation
        pyrig.rig.configs.base.yml.YmlConfigFile
            Parent class for .yml configuration files
    """

    UBUNTU_LATEST = "ubuntu-latest"
    WINDOWS_LATEST = "windows-latest"
    MACOS_LATEST = "macos-latest"

    def _configs(self) -> dict[str, Any]:
        """Build the complete workflow configuration.

        Returns:
            Dict with name, triggers, permissions, defaults, env, and jobs.
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
        """Check if the workflow configuration is correct.

        Handles the special case where workflow files cannot be empty.
        If empty, writes the full workflow config with job steps replaced
        by opt-out echo messages, allowing the workflow to be disabled
        while remaining valid YAML.

        Returns:
            True if configuration matches expected state.
        """
        correct = super().is_correct()

        if self.path().read_text(encoding="utf-8") == "":
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
    def jobs(self) -> dict[str, Any]:
        """Get the workflow jobs.

        Subclasses must implement this to define their jobs.

        Returns:
            Dict mapping job IDs to job configurations.
        """

    def workflow_triggers(self) -> dict[str, Any]:
        """Get the workflow triggers.

        Override to customize when the workflow runs.
        Default is manual workflow_dispatch only.

        Returns:
            Dict of trigger configurations.
        """
        return self.on_workflow_dispatch()

    def permissions(self) -> dict[str, Any]:
        """Get the workflow permissions.

        Override to request additional permissions.
        Default is no extra permissions.

        Returns:
            Dict of permission settings.
        """
        return {}

    def defaults(self) -> dict[str, Any]:
        """Get the workflow defaults.

        Override to customize default settings.
        Default uses bash shell.

        Returns:
            Dict of default settings.
        """
        return {"run": {"shell": "bash"}}

    def global_env(self) -> dict[str, Any]:
        """Get the global environment variables.

        Override to add environment variables.
        Default disables Python bytecode writing.

        Returns:
            Dict of environment variables.
        """
        return {
            "PYTHONDONTWRITEBYTECODE": 1,
            PackageManager.I.no_auto_install_env_var(): 1,
        }

    # WorkflowConfigFile Conventions
    # ----------------------------------------------------------------------------

    def workflow_name(self) -> str:
        """Generate a human-readable workflow name from the class name.

        Returns:
            Class name split on uppercase letters and joined with spaces.
        """
        name = self.__class__.__name__.removesuffix(WorkflowConfigFile.__name__)
        return " ".join(split_on_uppercase(name))

    def run_name(self) -> str:
        """Get the display name for workflow runs.

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
        outputs: dict[str, str] | None = None,
        steps: list[dict[str, Any]] | None = None,
        environment: str | None = None,
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
            environment: Environment name for registering deployments on GitHub.
            job: Existing job dict to update.

        Returns:
            Dict mapping job ID to job configuration.
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
        if environment is not None:
            job_config["environment"] = environment
        if outputs is not None:
            job_config["outputs"] = outputs
        if steps is not None:
            job_config["steps"] = steps
        job_config.update(job)
        return {name: job_config}

    def make_name_from_func(self, func: Callable[..., Any]) -> str:
        """Generate a human-readable name from a function.

        Args:
            func: Function to extract name from.

        Returns:
            Formatted name with prefix removed.
        """
        name = make_name_from_obj(func, split_on="_", join_on=" ", capitalize=True)
        prefix = split_on_uppercase(name)[0]
        return name.removeprefix(prefix).strip()

    def make_id_from_func(self, func: Callable[..., Any]) -> str:
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

    def on_workflow_dispatch(self) -> dict[str, Any]:
        """Create a manual workflow dispatch trigger.

        Returns:
            Trigger configuration for manual runs.
        """
        return {"workflow_dispatch": {}}

    def on_push(self, branches: list[str] | None = None) -> dict[str, Any]:
        """Create a push trigger.

        Args:
            branches: Branches to trigger on. Defaults to ["main"].

        Returns:
            Trigger configuration for push events.
        """
        if branches is None:
            branches = [VersionController.I.default_branch()]
        return {"push": {"branches": branches}}

    def on_schedule(self, cron: str) -> dict[str, Any]:
        """Create a scheduled trigger.

        Args:
            cron: Cron expression for the schedule.

        Returns:
            Trigger configuration for scheduled runs.
        """
        return {"schedule": [{"cron": cron}]}

    def on_pull_request(self, types: list[str] | None = None) -> dict[str, Any]:
        """Create a pull request trigger.

        Args:
            types: PR event types. Defaults to opened, synchronize, reopened.

        Returns:
            Trigger configuration for pull request events.
        """
        if types is None:
            types = ["opened", "synchronize", "reopened"]
        return {"pull_request": {"types": types}}

    def on_workflow_run(
        self, workflows: list[str], branches: list[str] | None = None
    ) -> dict[str, Any]:
        """Create a workflow run trigger.

        Args:
            workflows: WorkflowConfigFile names to trigger on.
            branches: Branches to filter on.

        Returns:
            Trigger configuration for workflow completion events.
        """
        config: dict[str, Any] = {"workflows": workflows, "types": ["completed"]}
        if branches is not None:
            config["branches"] = branches
        return {"workflow_run": config}

    # permissions

    def permission_content(self, permission: str = "read") -> dict[str, Any]:
        """Create a contents permission configuration.

        Args:
            permission: Permission level (read, write, none).

        Returns:
            Dict with contents permission.
        """
        return {"contents": permission}

    # Steps

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
        name = self.make_name_from_func(step_func)
        id_ = self.make_id_from_func(step_func)
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

    def strategy_matrix_os_and_python_version(
        self,
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
            python_version: List of Python versions. Defaults to supported versions.
            matrix: Additional matrix dimensions.
            strategy: Additional strategy options.

        Returns:
            Strategy configuration with Python version matrix.
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
            os: List of OS runners. Defaults to all major platforms.
            matrix: Additional matrix dimensions.
            strategy: Additional strategy options.

        Returns:
            Strategy configuration with OS matrix.
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
        """Finalize a strategy configuration.

        Args:
            strategy: Strategy configuration to finalize.

        Returns:
            Strategy with fail-fast defaulting to True.
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
            os: List of OS runners. Defaults to all major platforms.
            python_version: List of Python versions. Defaults to supported versions.
            matrix: Additional matrix dimensions.

        Returns:
            Matrix configuration with os and python-version.
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
            os: List of OS runners. Defaults to Ubuntu, Windows, macOS.
            matrix: Additional matrix dimensions.

        Returns:
            Matrix configuration with os.
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
            python_version: List of Python versions. Defaults to supported versions.
            matrix: Additional matrix dimensions.

        Returns:
            Matrix configuration with python-version.
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

        Args:
            matrix: Matrix dimensions.

        Returns:
            The matrix configuration unchanged.
        """
        return matrix

    # WorkflowConfigFile Steps
    # ----------------------------------------------------------------------------
    # Combined Steps

    def steps_core_setup(
        self,
        python_version: str | None = None,
        *,
        repo_token: bool = False,
        patch_version: bool = False,
    ) -> list[dict[str, Any]]:
        """Get the core setup steps for any workflow.

        Args:
            python_version: Python version to use. Defaults to latest supported.
            repo_token: Whether to use REPO_TOKEN for checkout.
            patch_version: Whether to patch the version.

        Returns:
            List with checkout and project setup steps.
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

    def steps_core_installed_setup(
        self,
        *,
        no_dev: bool = False,
        python_version: str | None = None,
        repo_token: bool = False,
        patch_version: bool = False,
    ) -> list[dict[str, Any]]:
        """Get core setup steps with dependency update and installation.

        Args:
            no_dev: Whether to skip dev dependencies.
            python_version: Python version to use. Defaults to latest supported.
            repo_token: Whether to use REPO_TOKEN for checkout.
            patch_version: Whether to patch the version.

        Returns:
            List with setup, dependency update, and dependency installation steps.
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

    def steps_core_matrix_setup(
        self,
        *,
        no_dev: bool = False,
        python_version: str | None = None,
        repo_token: bool = False,
        patch_version: bool = False,
    ) -> list[dict[str, Any]]:
        """Get core setup steps for matrix jobs.

        Args:
            no_dev: Whether to skip dev dependencies.
            python_version: Python version to use. If None (default),
                steps_core_installed_setup will use latest supported version.
            repo_token: Whether to use REPO_TOKEN for checkout.
            patch_version: Whether to patch the version.

        Returns:
            List with full setup steps for matrix execution.
        """
        return [
            *self.steps_core_installed_setup(
                python_version=python_version,
                repo_token=repo_token,
                no_dev=no_dev,
                patch_version=patch_version,
            ),
        ]

    # Single Step

    def step_opt_out_of_workflow(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that opts out of the workflow.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that echoes an opt-out message.
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
        """Create a step that aggregates matrix job results.

        Args:
            step: Existing step dict to update.

        Returns:
            Step configuration for result aggregation.
        """
        return self.step(
            step_func=self.step_aggregate_jobs,
            run="echo 'Aggregating jobs into one job.'",
            step=step,
        )

    def step_no_builder_defined(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a placeholder step when no builders are defined.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that echoes a skip message.
        """
        return self.step(
            step_func=self.step_no_builder_defined,
            run="echo 'No non-abstract builders defined. Skipping build.'",
            step=step,
        )

    def step_install_container_engine(
        self,
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
        """Create a step that builds the container image.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that builds the container image.
        """
        return self.step(
            step_func=self.step_build_container_image,
            run=str(
                ContainerEngine.I.build_args(
                    project_name=PyprojectConfigFile.I.project_name()
                )
            ),
            step=step,
        )

    def step_save_container_image(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that saves the container image to a file.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that saves the container image.
        """
        image_file = Path(f"{PyprojectConfigFile.I.project_name()}.tar")
        image_path = Path(BuilderConfigFile.dist_dir_name()) / image_file
        return self.step(
            step_func=self.step_save_container_image,
            run=str(
                ContainerEngine.I.save_args(
                    image_file=image_file,
                    image_path=image_path,
                )
            ),
            step=step,
        )

    def step_run_tests(
        self,
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
        if src_package_is_pyrig():
            step.setdefault("env", {})["REPO_TOKEN"] = self.insert_repo_token()
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
        fail_ci_if_error = self.insert_var(
            "${{ secrets.CODECOV_TOKEN && 'true' || 'false' }}"
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

    def step_patch_version(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that bumps the patch version.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that increments version and stages pyproject.toml.
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
        """Create a step that stages the version bump commit.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that stages pyproject.toml.
        """
        return self.step(
            step_func=self.step_add_version_bump_to_version_control,
            run=str(VersionController.I.add_pyproject_toml_and_lock_file_args()),
            step=step,
        )

    def step_add_dependency_updates_to_version_control(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that stages dependency file changes.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that stages pyproject.toml and uv.lock.
        """
        return self.step(
            step_func=self.step_add_dependency_updates_to_version_control,
            run=str(VersionController.I.add_pyproject_toml_and_lock_file_args()),
            step=step,
        )

    def step_checkout_repository(
        self,
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
        """Create a step that configures git user for commits.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that sets git user.email and user.name.
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

    def step_setup_python(
        self,
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
                PyprojectConfigFile.I.latest_possible_python_version(level="minor")
            )

        step.setdefault("with", {})["python-version"] = python_version
        return self.step(
            step_func=self.step_setup_python,
            uses="actions/setup-python@main",
            step=step,
        )

    def step_setup_package_manager(
        self,
        *,
        python_version: str,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that sets up the project package manager (uv).

        Args:
            python_version: Python version to configure.
            step: Existing step dict to update.

        Returns:
            Step using astral-sh/setup-uv.
        """
        return self.step(
            step_func=self.step_setup_package_manager,
            uses="astral-sh/setup-uv@main",
            with_={"python-version": python_version},
            step=step,
        )

    def step_build_wheel(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that builds the Python wheel.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs uv build.
        """
        return self.step(
            step_func=self.step_build_wheel,
            run=str(PackageManager.I.build_args()),
            step=step,
        )

    def step_publish_to_pypi(
        self,
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
        run = str(PackageManager.I.publish_args(token=self.insert_pypi_token()))
        run_if = self.run_if_condition(run, self.insert_pypi_token())
        return self.step(
            step_func=self.step_publish_to_pypi,
            run=run_if,
            step=step,
        )

    def step_build_documentation(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that builds the project documentation.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that builds the project documentation.
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
        """Create a step that enables GitHub Pages.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that enables GitHub Pages.
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
        """Create a step that uploads the documentation to GitHub Pages.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that uploads the documentation to GitHub Pages.
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
        """Create a step that deploys the documentation to GitHub Pages.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that deploys documentation to GitHub Pages.
        """
        return self.step(
            step_func=self.step_deploy_documentation,
            uses="actions/deploy-pages@main",
            step=step,
        )

    def step_update_dependencies(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that updates the dependencies.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs uv lock --upgrade.
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
        """Create a step that installs Python dependencies.

        Args:
            no_dev: Whether to skip dev dependencies.
            step: Existing step dict to update.

        Returns:
            Step that runs uv sync.
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

    def step_protect_repository(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that applies repository protection rules.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs the pyrig protect-repo command.
        """
        return self.step(
            step_func=self.step_protect_repository,
            run=str(PackageManager.I.run_args(*Pyrigger.I.cmd_args(cmd=protect_repo))),
            env={"REPO_TOKEN": self.insert_repo_token()},
            step=step,
        )

    def step_run_pre_commit_hooks(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that runs prek hooks.

        Ensures code quality checks pass before commits. Also useful
        for ensuring git stash pop doesn't fail when there are no changes.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs prek on all files.
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
        """Create a step that audits installed dependencies for known vulnerabilities.

        Runs pip-audit via uv (``uv run pip-audit``) so the audit uses the
        workflow's installed environment.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs pip-audit.
        """
        return self.step(
            step_func=self.step_run_dependency_audit,
            run=str(PackageManager.I.run_args(*DependencyAuditor.I.audit_args())),
            step=step,
        )

    def step_commit_added_changes(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that commits staged changes.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that commits with [skip ci] prefix.
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
        """Create a step that pushes commits to the remote.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs git push.
        """
        return self.step(
            step_func=self.step_push_commits,
            run=str(VersionController.I.push_args()),
            step=step,
        )

    def step_create_and_push_tag(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that creates and pushes a version tag.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that creates a git tag and pushes it.
        """
        return self.step(
            step_func=self.step_create_and_push_tag,
            run=str(VersionController.I.tag_args(tag=self.insert_version()))
            + " && "
            + str(VersionController.I.push_origin_tag_args(tag=self.insert_version())),
            step=step,
        )

    def step_upload_artifacts(
        self,
        *,
        name: str | None = None,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that uploads build artifacts.

        Args:
            name: Artifact name. Defaults to package-os format.
            step: Existing step dict to update.

        Returns:
            Step using actions/upload-artifact.
        """
        if name is None:
            name = self.insert_artifact_name()
        return self.step(
            step_func=self.step_upload_artifacts,
            uses="actions/upload-artifact@main",
            with_={"name": name, "path": BuilderConfigFile.dist_dir_name()},
            step=step,
        )

    def step_build_artifacts(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that builds project artifacts.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that runs the pyrig build command.
        """
        return self.step(
            step_func=self.step_build_artifacts,
            run=str(PackageManager.I.run_args(*Pyrigger.I.cmd_args(cmd=build))),
            step=step,
        )

    def step_download_artifacts(
        self,
        *,
        name: str | None = None,
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
        with_: dict[str, Any] = {"path": BuilderConfigFile.dist_dir_name()}
        if name is not None:
            with_["name"] = name
        with_["merge-multiple"] = "true"
        return self.step(
            step_func=self.step_download_artifacts,
            uses="actions/download-artifact@main",
            with_=with_,
            step=step,
        )

    def step_download_artifacts_from_workflow_run(
        self,
        *,
        name: str | None = None,
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
            "path": BuilderConfigFile.dist_dir_name(),
            "run-id": self.insert_workflow_run_id(),
            "github-token": self.insert_github_token(),
        }
        if name is not None:
            with_["name"] = name
        with_["merge-multiple"] = "true"
        return self.step(
            step_func=self.step_download_artifacts_from_workflow_run,
            uses="actions/download-artifact@main",
            with_=with_,
            step=step,
        )

    def step_build_changelog(
        self,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a step that generates a changelog.

        Args:
            step: Existing step dict to update.

        Returns:
            Step using release-changelog-builder-action.
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
        """Create a step that extracts the version to GITHUB_OUTPUT.

        Args:
            step: Existing step dict to update.

        Returns:
            Step that outputs the version for later steps.
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
        """Create a step that creates a GitHub release.

        Args:
            step: Existing step dict to update.
            artifacts_pattern: Glob pattern for release artifacts.

        Returns:
            Step using ncipollo/release-action.
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

    # Insertions
    # ----------------------------------------------------------------------------

    def insert_var(self, var: str) -> str:
        """Wrap a variable in GitHub Actions expression syntax.

        Args:
            var: Variable expression to wrap.

        Returns:
            GitHub Actions expression for the variable.
        """
        # remove existing wrapping if it exists
        var = var.strip().removeprefix("${{").removesuffix("}}").strip()
        return f"${{{{ {var} }}}}"

    def insert_repo_token(self) -> str:
        """Get the GitHub expression for REPO_TOKEN secret.

        Returns:
            GitHub Actions expression for secrets.REPO_TOKEN.
        """
        return self.insert_var("secrets.REPO_TOKEN")

    def insert_pypi_token(self) -> str:
        """Get the GitHub expression for PYPI_TOKEN secret.

        Returns:
            GitHub Actions expression for secrets.PYPI_TOKEN.
        """
        return self.insert_var("secrets.PYPI_TOKEN")

    def insert_version(self) -> str:
        """Get a shell expression for the current version.

        Returns:
            Shell command that outputs the version with v prefix.
        """
        script = str(PackageManager.I.version_short_args())
        return f"v$({script})"

    def insert_version_from_extract_version_step(self) -> str:
        """Get the GitHub expression for version from extract step.

        Returns:
            GitHub Actions expression referencing the extract_version output.
        """
        # make dynamic with self.make_id_from_func(self.step_extract_version)
        return self.insert_var(
            f"steps.{self.make_id_from_func(self.step_extract_version)}.outputs.version"
        )

    def insert_changelog(self) -> str:
        """Get the GitHub expression for changelog from build step.

        Returns:
            GitHub Actions expression referencing the build_changelog output.
        """
        return self.insert_var(
            f"steps.{self.make_id_from_func(self.step_build_changelog)}.outputs.changelog"
        )

    def insert_github_token(self) -> str:
        """Get the GitHub expression for GITHUB_TOKEN.

        Returns:
            GitHub Actions expression for secrets.GITHUB_TOKEN.
        """
        return self.insert_var("secrets.GITHUB_TOKEN")

    def insert_codecov_token(self) -> str:
        """Get the GitHub expression for CODECOV_TOKEN.

        Returns:
            GitHub Actions expression for secrets.CODECOV_TOKEN.
        """
        return self.insert_var("secrets.CODECOV_TOKEN")

    def insert_repository_name(self) -> str:
        """Get the GitHub expression for repository name.

        Returns:
            GitHub Actions expression for the repository name.
        """
        return self.insert_var("github.event.repository.name")

    def insert_ref_name(self) -> str:
        """Get the GitHub expression for the ref name.

        Returns:
            GitHub Actions expression for github.ref_name.
        """
        return self.insert_var("github.ref_name")

    def insert_repository_owner(self) -> str:
        """Get the GitHub expression for repository owner.

        Returns:
            GitHub Actions expression for github.repository_owner.
        """
        return self.insert_var("github.repository_owner")

    def insert_workflow_run_id(self) -> str:
        """Get the GitHub expression for triggering workflow run ID.

        Used when downloading artifacts from the workflow that triggered
        this workflow via workflow_run event.

        Returns:
            GitHub Actions expression for github.event.workflow_run.id.
        """
        return self.insert_var("github.event.workflow_run.id")

    def insert_os(self) -> str:
        """Get the GitHub expression for runner OS.

        Returns:
            GitHub Actions expression for runner.os.
        """
        return self.insert_var("runner.os")

    def insert_matrix_os(self) -> str:
        """Get the GitHub expression for matrix OS value.

        Returns:
            GitHub Actions expression for matrix.os.
        """
        return self.insert_var("matrix.os")

    def insert_matrix_python_version(self) -> str:
        """Get the GitHub expression for matrix Python version.

        Returns:
            GitHub Actions expression for matrix.python-version.
        """
        return self.insert_var("matrix.python-version")

    def insert_artifact_name(self) -> str:
        """Generate an artifact name based on package and OS.

        Returns:
            Artifact name in format: package-os.
        """
        return f"{PyprojectConfigFile.I.project_name()}-{self.insert_os()}"

    # ifs
    # ----------------------------------------------------------------------------

    def combined_if(self, *conditions: str, operator: str) -> str:
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
        return self.insert_var(f" {operator} ".join(bare_conditions))

    def if_matrix_is_not_os(self, os: str) -> str:
        """Create a condition for not matching a specific OS.

        Args:
            os: OS runner label to not match.

        Returns:
            Condition expression for matrix.os comparison.
        """
        return self.insert_var(f"matrix.os != '{os}'")

    def if_not_triggered_by_cron(self) -> str:
        """Create a condition for not being triggered by cron.

        Returns:
            GitHub Actions expression checking event name.
        """
        return self.insert_var("github.event_name != 'schedule'")

    def if_workflow_run_is_success(self) -> str:
        """Create a condition for successful workflow run.

        Returns:
            GitHub Actions expression checking workflow_run conclusion.
        """
        return self.insert_var("github.event.workflow_run.conclusion == 'success'")

    def if_workflow_run_is_not_cron_triggered(self) -> str:
        """Create a condition for the triggering workflow run not being cron.

        Returns:
            GitHub Actions expression checking workflow_run event name.
        """
        return self.insert_var("github.event.workflow_run.event != 'schedule'")

    def if_pypi_token_configured(self) -> str:
        """Create a condition for PYPI_TOKEN being configured.

        Returns:
            GitHub Actions expression checking for PYPI_TOKEN.
        """
        return self.insert_var("secrets.PYPI_TOKEN != ''")

    def if_codecov_token_configured(self) -> str:
        """Create a condition for CODECOV_TOKEN being configured.

        Returns:
            GitHub Actions expression checking for CODECOV_TOKEN.
        """
        return self.insert_var("secrets.CODECOV_TOKEN != ''")

    # Runs
    # ----------------------------------------------------------------------------

    def run_if_condition(self, run: str, condition: str) -> str:
        """Return a run command that only runs if condition is true.

        Args:
            run: Command to run.
            condition: Condition expression.

        Returns:
            Shell script that runs the command conditionally.
        """
        condition_check = self.insert_var(condition)
        # make a script that runs the command if the token is configured
        # and echos a message if it is not
        condition_as_str = (
            condition_check.strip().removeprefix("${{").removesuffix("}}").strip()
        )
        msg = f"Skipping step due to failed condition: {condition_as_str}."
        return f'if [ {condition_check} ]; then {run}; else echo "{msg}"; fi'
