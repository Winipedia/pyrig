"""Complete project initialization orchestration.

Transforms a basic Python project into a fully-configured, production-ready
pyrig project through a comprehensive automated sequence.

The initialization process executes steps in a specific order to ensure all
dependencies and configurations are properly established. Each step is
implemented as a separate function that returns Args objects, which are then
executed sequentially via PackageManager. If any step fails, the process stops
immediately.

The initialization steps execute in the following order:
    - Initializing version control (git init)
    - Adding dev dependencies (uv add --group dev)
    - Syncing venv (uv sync)
    - Creating priority config files (LICENSE, pyproject.toml, etc.)
    - Syncing venv again (apply new configs)
    - Creating project root (all remaining config files)
    - Creating test files (test skeletons for all source code)
    - Installing prek hooks (prek install)
    - Adding all files to version control (git add .)
    - Running prek hooks (format/lint all files)
    - Running tests (validate everything works)
    - Committing initial changes (create initial git commit)

Note:
    This process is designed for initial setup, not repeated execution.
    Individual steps (mkroot, mktests) are idempotent, but the full sequence
    is optimized for first-time setup.
"""

from collections.abc import Callable
from typing import Any

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
)

from pyrig.rig.cli.subcommands import mkroot, mktests
from pyrig.rig.tools.base.base import Tool
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pre_committer import (
    PreCommitter,
)
from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.version_controller import VersionController
from pyrig.src.processes import Args
from pyrig.src.string_ import make_name_from_obj


def initializing_version_control() -> Args:
    """Get args to initialize version control.

    Returns Args for initializing a git repository via `git init`.

    Returns:
        Args object for initializing version control.
    """
    return VersionController.L.init_args()


def adding_dev_dependencies() -> Args:
    """Get args to install development dependencies.

    Returns Args for adding pyrig's standard dev dependencies to pyproject.toml
    via `uv add --group dev`.

    Returns:
        Args object for adding dev dependencies.
    """
    return PackageManager.L.add_dev_dependencies_args(
        *Tool.subclasses_dev_dependencies()
    )


def creating_priority_config_files() -> Args:
    """Get args to create essential configuration files.

    Returns Args for creating high-priority config files (pyproject.toml,
    .gitignore, LICENSE) that other initialization steps depend on via
    `pyrig mkroot --priority`.

    Returns:
        Args object for creating priority config files.
    """
    # local imports to avoid failure on init when dev deps are not installed yet.
    return Pyrigger.L.cmd_args("--priority", cmd=mkroot)


def syncing_venv() -> Args:
    """Get args to sync virtual environment with dependencies.

    Returns Args for installing all dependencies from pyproject.toml via
    `uv sync`. Run twice during initialization: after adding dev dependencies
    and after creating priority config files.

    Returns:
        Args object for syncing the virtual environment.
    """
    return PackageManager.L.install_dependencies_args()


def creating_project_root() -> Args:
    """Get args to create complete project structure and config files.

    Returns Args for generating all remaining configuration files and directory
    structure via `pyrig mkroot`.

    Returns:
        Args object for creating the project root.
    """
    return Pyrigger.L.cmd_args(cmd=mkroot)


def creating_test_files() -> Args:
    """Get args to generate test skeleton files for all source code.

    Returns Args for creating test files mirroring the source package structure
    with NotImplementedError placeholders via `pyrig mktests`.

    Returns:
        Args object for creating test files.
    """
    return Pyrigger.L.cmd_args(cmd=mktests)


def install_pre_commit_hooks() -> Args:
    """Get args to install prek hooks.

    Returns Args for installing prek hooks into the git repository via
    `prek install`.

    Returns:
        Args object for installing prek hooks.
    """
    return PreCommitter.L.install_args()


def add_all_files_to_version_control() -> Args:
    """Get args to add all files to version control.

    Returns Args for staging all files for commit via `git add .`.

    Returns:
        Args object for adding all files to version control.
    """
    return VersionController.L.add_all_args()


def running_pre_commit_hooks() -> Args:
    """Get args to run prek hooks on all files.

    Returns Args for running formatters/linters on all files to ensure the
    codebase follows style guidelines via `prek run --all-files`.

    Returns:
        Args object for running prek hooks.
    """
    return PreCommitter.L.run_all_files_args()


def running_tests() -> Args:
    """Get args to run the complete test suite.

    Returns Args for validating that all generated code is syntactically correct
    and the project is properly configured via `pytest`.

    Returns:
        Args object for running tests.
    """
    return ProjectTester.L.test_args()


def committing_initial_changes() -> Args:
    """Get args to create initial git commit with all changes.

    Returns Args for committing all configuration files, test skeletons, and
    formatting changes with the message "pyrig: Initial commit".

    Returns:
        Args object for committing initial changes.
    """
    # changes were added by the run prek hooks step
    return VersionController.L.commit_no_verify_args(
        msg=f"{Pyrigger.name()}: Initial commit"
    )


def setup_steps() -> list[Callable[..., Any]]:
    """Return the ordered list of setup step functions for project initialization.

    Each function in the returned list takes no arguments and returns an Args
    object that can be executed via PackageManager.

    Returns:
        Ordered list of setup step functions.
    """
    return [
        initializing_version_control,
        adding_dev_dependencies,
        syncing_venv,
        creating_priority_config_files,
        syncing_venv,
        creating_project_root,
        creating_test_files,
        install_pre_commit_hooks,
        add_all_files_to_version_control,
        running_pre_commit_hooks,
        running_tests,
        committing_initial_changes,
    ]


def init_project() -> None:
    """Initialize a pyrig project by running all setup steps sequentially.

    Executes the complete initialization sequence to transform a basic Python
    project into a fully-configured, production-ready pyrig project.

    Each step returns an Args object that is executed via PackageManager. Steps
    are executed in order with a progress bar that updates after each step
    completes. If any step fails, the process stops immediately.

    Note:
        This function should be run once when setting up a new project.
    """
    steps = setup_steps()
    total = len(steps)
    with Progress(
        TextColumn("[bold]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
    ) as progress:
        task = progress.add_task("Initializing project", total=total)
        for step in steps:
            step_name = make_name_from_obj(step, join_on=" ")
            progress.update(task, description=step_name)
            PackageManager.L.run_args(*step()).run()
            progress.advance(task)
        progress.update(task, description="[green]Initialization complete!")
