"""Contains base utilities for git workflows."""

from abc import abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar

import pyrig
from pyrig.dev.artifacts.builder.base.base import Builder
from pyrig.dev.cli.subcommands import build, protect_repo
from pyrig.dev.configs.base.base import YamlConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.package import DependencyGraph, get_src_package
from pyrig.src.project.poetry.poetry import get_poetry_run_pyrig_cli_cmd_script
from pyrig.src.string import (
    make_name_from_obj,
    split_on_uppercase,
)


class Workflow(YamlConfigFile):
    """Base class for workflows."""

    UBUNTU_LATEST = "ubuntu-latest"
    WINDOWS_LATEST = "windows-latest"
    MACOS_LATEST = "macos-latest"

    ARTIFACTS_DIR_NAME = Builder.ARTIFACTS_DIR_NAME
    ARTIFACTS_PATTERN = f"{ARTIFACTS_DIR_NAME}/*"

    EMPTY_CONFIG: ClassVar[dict[str, Any]] = {
        "on": {
            "workflow_dispatch": {},
        },
        "jobs": {
            "empty": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Empty Step",
                        "run": "echo 'Empty Step'",
                    }
                ],
            },
        },
    }

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the workflow config."""
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
        """Get the path to the config file."""
        return Path(".github/workflows")

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the config is correct.

        Needs some special handling since workflow files cannot be empty.
        We need a workflow that will never trigger and even if doesnt do anything.
        """
        correct = super().is_correct()
        if cls.get_path().read_text(encoding="utf-8") == "":
            # dump a dispatch in there for on and an empty job for jobs
            cls.dump(cls.EMPTY_CONFIG)

        return correct or cls.load() == cls.EMPTY_CONFIG

    # Overridable Workflow Parts
    # ----------------------------------------------------------------------------
    @classmethod
    @abstractmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Get the workflow jobs."""

    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Get the workflow triggers.

        Can be overriden. Standard is workflow_dispatch.
        """
        return cls.on_workflow_dispatch()

    @classmethod
    def get_permissions(cls) -> dict[str, Any]:
        """Get the workflow permissions. Can be overriden.

        Standard is no extra permissions.
        """
        return {}

    @classmethod
    def get_defaults(cls) -> dict[str, Any]:
        """Get the workflow defaults. Can be overriden.

        Standard is bash.
        """
        return {"run": {"shell": "bash"}}

    @classmethod
    def get_global_env(cls) -> dict[str, Any]:
        """Get the global env. Can be overriden.

        Standard is no global env.
        """
        return {"PYTHONDONTWRITEBYTECODE": 1}

    # Workflow Conventions
    # ----------------------------------------------------------------------------
    @classmethod
    def get_workflow_name(cls) -> str:
        """Get the workflow name."""
        return " ".join(split_on_uppercase(cls.__name__))

    @classmethod
    def get_run_name(cls) -> str:
        """Get the run name."""
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
        """Get a job.

        Args:
        job_func: The function that represents the job. Used to generate the name.
        job: The job to update. Defaults to a new job.
        needs: The needs of the job.
        strategy: The strategy of the job. like matrix
        permissions: The permissions of the job.
        runs_on: The runs-on of the job. Defaults to ubuntu-latest.
        if_condition: The if condition of the job.
        steps: The steps of the job.

        Returns:
        The job.
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
        """Make a name from a function."""
        name = make_name_from_obj(func, split_on="_", join_on=" ", capitalize=True)
        prefix = split_on_uppercase(name)[0]
        return name.removeprefix(prefix).strip()

    @classmethod
    def make_id_from_func(cls, func: Callable[..., Any]) -> str:
        """Make an id from a function."""
        name = func.__name__
        prefix = name.split("_")[0]
        return name.removeprefix(f"{prefix}_")

    # triggers
    @classmethod
    def on_workflow_dispatch(cls) -> dict[str, Any]:
        """Get the workflow dispatch trigger."""
        return {"workflow_dispatch": {}}

    @classmethod
    def on_push(cls, branches: list[str] | None = None) -> dict[str, Any]:
        """Get the push trigger."""
        if branches is None:
            branches = ["main"]
        return {"push": {"branches": branches}}

    @classmethod
    def on_schedule(cls, cron: str) -> dict[str, Any]:
        """Get the schedule trigger."""
        return {"schedule": [{"cron": cron}]}

    @classmethod
    def on_pull_request(cls, types: list[str] | None = None) -> dict[str, Any]:
        """Get the pull request trigger."""
        if types is None:
            types = ["opened", "synchronize", "reopened"]
        return {"pull_request": {"types": types}}

    @classmethod
    def on_workflow_run(cls, workflows: list[str] | None = None) -> dict[str, Any]:
        """Get the workflow run trigger."""
        if workflows is None:
            workflows = [cls.get_workflow_name()]
        return {"workflow_run": {"workflows": workflows, "types": ["completed"]}}

    # permissions
    @classmethod
    def permission_content(cls, permission: str = "read") -> dict[str, Any]:
        """Get the content read permission."""
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
        """Get a step.

        Args:
        step_func: The function that represents the step. Used to generate the name.
        run: The run command.
        if_condition: The if condition.
        uses: The uses command.
        with_: The with command.
        env: The env command.
        step: The step to update. Defaults to a new step.

        Returns:
        The step.
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
        """Get a strategy for os and python version."""
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
        """Get a strategy for python version."""
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
        """Get a strategy for os."""
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
        """Get a matrix strategy."""
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
        """Get a strategy."""
        strategy["fail-fast"] = strategy.pop("fail-fast", True)
        return strategy

    @classmethod
    def matrix_os_and_python_version(
        cls,
        os: list[str] | None = None,
        python_version: list[str] | None = None,
        matrix: dict[str, list[Any]] | None = None,
    ) -> dict[str, Any]:
        """Get a matrix for os and python version."""
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
        """Get a matrix for os."""
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
        """Get a matrix for python version."""
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
        """Get a matrix."""
        return matrix

    # Workflow Steps
    # ----------------------------------------------------------------------------
    # Combined Steps
    @classmethod
    def steps_core_setup(
        cls, python_version: str | None = None, *, repo_token: bool = False
    ) -> list[dict[str, Any]]:
        """Get the core setup steps."""
        return [
            cls.step_checkout_repository(repo_token=repo_token),
            cls.step_setup_python(python_version=python_version),
            cls.step_setup_poetry(),
        ]

    @classmethod
    def steps_core_installed_setup(
        cls, python_version: str | None = None, *, repo_token: bool = False
    ) -> list[dict[str, Any]]:
        """Get the core setup steps."""
        return [
            *cls.steps_core_setup(python_version=python_version, repo_token=repo_token),
            cls.step_add_poetry_to_windows_path(),
            cls.step_install_python_dependencies(),
            *cls.steps_configure_keyring_if_needed(),
            cls.step_update_dependencies(),
            cls.step_add_dependency_updates_to_git(),
        ]

    @classmethod
    def steps_core_matrix_setup(
        cls, python_version: str | None = None, *, repo_token: bool = False
    ) -> list[dict[str, Any]]:
        """Get the core matrix setup steps."""
        return [
            *cls.steps_core_installed_setup(
                python_version=python_version, repo_token=repo_token
            ),
        ]

    @classmethod
    def steps_configure_keyring_if_needed(cls) -> list[dict[str, Any]]:
        """Get the keyring steps if keyring is in dependencies."""
        steps: list[dict[str, Any]] = []
        if "keyring" in DependencyGraph.get_all_dependencies():
            steps.append(cls.step_setup_keyring())
        return steps

    # Single Step
    @classmethod
    def step_aggregate_matrix_results(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the aggregate matrix results step."""
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
        """Get the no build script step."""
        return cls.get_step(
            step_func=cls.step_no_builder_defined,
            run="echo 'No non-abstract builders defined. Skipping build.'",
            step=step,
        )

    @classmethod
    def step_run_tests(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the run tests step."""
        if step is None:
            step = {}
        if PyprojectConfigFile.get_package_name() == pyrig.__name__:
            step.setdefault("env", {})["REPO_TOKEN"] = cls.insert_repo_token()
        return cls.get_step(
            step_func=cls.step_run_tests,
            run="poetry run pytest --log-cli-level=INFO",
            step=step,
        )

    @classmethod
    def step_patch_version(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the patch version step."""
        return cls.get_step(
            step_func=cls.step_patch_version,
            run="poetry version patch && git add pyproject.toml",
            step=step,
        )

    @classmethod
    def step_update_dependencies(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the update dependencies step."""
        return cls.get_step(
            step_func=cls.step_update_dependencies,
            run="poetry update --with dev",
            step=step,
        )

    @classmethod
    def step_add_dependency_updates_to_git(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the add dependency updates to git step."""
        return cls.get_step(
            step_func=cls.step_add_dependency_updates_to_git,
            run="git add pyproject.toml poetry.lock",
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
        """Get the checkout step."""
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
        """Get the setup git step."""
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
        """Get the setup python step."""
        if step is None:
            step = {}
        if python_version is None:
            python_version = str(
                PyprojectConfigFile.get_latest_possible_python_version()
            )

        step.setdefault("with", {})["python-version"] = python_version
        return cls.get_step(
            step_func=cls.step_setup_python,
            uses="actions/setup-python@main",
            step=step,
        )

    @classmethod
    def step_setup_poetry(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the setup poetry step."""
        return cls.get_step(
            step_func=cls.step_setup_poetry,
            uses="snok/install-poetry@main",
            step=step,
        )

    @classmethod
    def step_add_poetry_to_windows_path(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the add poetry to path step."""
        return cls.get_step(
            step_func=cls.step_add_poetry_to_windows_path,
            run="echo 'C:/Users/runneradmin/.local/bin' >> $GITHUB_PATH",
            if_condition=f"{cls.insert_os()} == 'Windows'",
            step=step,
        )

    @classmethod
    def step_add_pypi_token_to_poetry(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the add pypi token to poetry step."""
        return cls.get_step(
            step_func=cls.step_add_pypi_token_to_poetry,
            run="poetry config pypi-token.pypi ${{ secrets.PYPI_TOKEN }}",
            step=step,
        )

    @classmethod
    def step_publish_to_pypi(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the publish to pypi step."""
        return cls.get_step(
            step_func=cls.step_publish_to_pypi,
            run="poetry publish --build",
            step=step,
        )

    @classmethod
    def step_install_python_dependencies(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the install dependencies step."""
        return cls.get_step(
            step_func=cls.step_install_python_dependencies,
            run="poetry install --with dev",
            step=step,
        )

    @classmethod
    def step_setup_keyring(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the setup keyring step."""
        return cls.get_step(
            step_func=cls.step_setup_keyring,
            run='poetry run pip install keyrings.alt && poetry run python -c "import keyring; from keyrings.alt.file import PlaintextKeyring; keyring.set_keyring(PlaintextKeyring());"',  # noqa: E501
            step=step,
        )

    @classmethod
    def step_protect_repository(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the protect repository step."""
        return cls.get_step(
            step_func=cls.step_protect_repository,
            run=get_poetry_run_pyrig_cli_cmd_script(
                cmd=protect_repo,
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
        """Get the run pre-commit hooks step.

        Patching version is useful to have at least a minimal version bump when
        creating a release and it also makes sure git stash pop does not fail when
        there are no changes.
        """
        return cls.get_step(
            step_func=cls.step_run_pre_commit_hooks,
            run="poetry run pre-commit run --all-files",
            step=step,
        )

    @classmethod
    def step_add_version_patch(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the add version patch step."""
        return cls.get_step(
            step_func=cls.step_add_version_patch,
            run="poetry version patch && git add pyproject.toml",
            step=step,
        )

    @classmethod
    def step_commit_added_changes(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the commit changes step."""
        return cls.get_step(
            step_func=cls.step_commit_added_changes,
            run="git commit --no-verify -m '[skip ci] CI/CD: Committing possible added changes (e.g.: pyproject.toml and poetry.lock)'",  # noqa: E501
            step=step,
        )

    @classmethod
    def step_push_commits(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the push changes step."""
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
        """Get the tag and push step."""
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
        """Get the create folder step."""
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
        """Get the create artifacts folder step."""
        return cls.step_create_folder(folder=folder, step=step)

    @classmethod
    def step_upload_artifacts(
        cls,
        *,
        name: str | None = None,
        path: str | Path = ARTIFACTS_DIR_NAME,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the upload artifacts step."""
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
        """Get the build artifacts step."""
        return cls.get_step(
            step_func=cls.step_build_artifacts,
            run=get_poetry_run_pyrig_cli_cmd_script(build),
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
        """Get the download artifacts step."""
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
    def step_build_changelog(
        cls,
        *,
        step: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the build changelog step."""
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
        """Get the extract version step."""
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
        """Get the create release step."""
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
        """Insert the repository token."""
        return "${{ secrets.REPO_TOKEN }}"

    @classmethod
    def insert_version(cls) -> str:
        """Insert the version."""
        return "v$(poetry version -s)"

    @classmethod
    def insert_version_from_extract_version_step(cls) -> str:
        """Insert the version from the extract version step."""
        # make dynamic with cls.make_id_from_func(cls.step_extract_version)
        return (
            "${{ "
            f"steps.{cls.make_id_from_func(cls.step_extract_version)}.outputs.version"
            " }}"
        )

    @classmethod
    def insert_changelog(cls) -> str:
        """Insert the changelog."""
        return (
            "${{ "
            f"steps.{cls.make_id_from_func(cls.step_build_changelog)}.outputs.changelog"
            " }}"
        )

    @classmethod
    def insert_github_token(cls) -> str:
        """Insert the GitHub token."""
        return "${{ secrets.GITHUB_TOKEN }}"

    @classmethod
    def insert_repository_name(cls) -> str:
        """Insert the repository name."""
        return "${{ github.event.repository.name }}"

    @classmethod
    def insert_ref_name(cls) -> str:
        """Insert the ref name."""
        return "${{ github.ref_name }}"

    @classmethod
    def insert_repository_ownwer(cls) -> str:
        """Insert the repository owner."""
        return "${{ github.repository_owner }}"

    @classmethod
    def insert_os(cls) -> str:
        """Insert the os."""
        return "${{ runner.os }}"

    @classmethod
    def insert_matrix_os(cls) -> str:
        """Insert the matrix os."""
        return "${{ matrix.os }}"

    @classmethod
    def insert_matrix_python_version(cls) -> str:
        """Insert the matrix python version."""
        return "${{ matrix.python-version }}"

    @classmethod
    def insert_artifact_name(cls) -> str:
        """Insert the artifact name."""
        return f"{get_src_package().__name__}-{cls.insert_os()}"

    # ifs
    @classmethod
    def if_matrix_is_os(cls, os: str) -> str:
        """Insert the matrix os."""
        return f"matrix.os == '{os}'"

    @classmethod
    def if_matrix_is_python_version(cls, python_version: str) -> str:
        """Insert the matrix python version."""
        return f"matrix.python-version == '{python_version}'"

    @classmethod
    def if_matrix_is_os_and_python_version(cls, os: str, python_version: str) -> str:
        """Insert the matrix os and python version."""
        return f"{cls.if_matrix_is_os(os)} && {cls.if_matrix_is_python_version(python_version)}"  # noqa: E501

    @classmethod
    def if_matrix_is_latest_python_version(cls) -> str:
        """Insert the matrix latest python version."""
        return cls.if_matrix_is_python_version(
            str(PyprojectConfigFile.get_latest_possible_python_version())
        )

    @classmethod
    def if_matrix_is_os_and_latest_python_version(cls, os: str) -> str:
        """Insert the matrix os and latest python version."""
        return cls.if_matrix_is_os_and_python_version(
            os, str(PyprojectConfigFile.get_latest_possible_python_version())
        )

    @classmethod
    def if_workflow_run_is_success(cls) -> str:
        """Insert the if workflow run is success."""
        return "${{ github.event.workflow_run.conclusion == 'success' }}"
