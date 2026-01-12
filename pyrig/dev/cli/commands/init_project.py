"""Complete project initialization orchestration.

Transforms a basic Python project into a fully-configured, production-ready
pyrig project through a comprehensive automated sequence.

The initialization process executes steps in a specific order to ensure all
dependencies and configurations are properly established. Each step is
implemented as a separate function that returns Args objects, which are then
executed sequentially via PackageManager. If any step fails, the process stops
immediately.

Initialization Steps:
    1. Adding dev dependencies (uv add --group dev)
    2. Syncing venv (uv sync)
    3. Creating priority config files (LICENSE, pyproject.toml, etc.)
    4. Syncing venv again (apply new configs)
    5. Creating project root (all remaining config files)
    6. Creating test files (test skeletons for all source code)
    7. Installing pre-commit hooks (pre-commit install)
    8. Adding all files to version control (git add .)
    9. Running pre-commit hooks (format/lint all files)
    10. Running tests (validate everything works)
    11. Committing initial changes (create initial git commit)

Note:
    This process is designed for initial setup, not repeated execution.
    Individual steps (mkroot, mktests) are idempotent, but the full sequence
    is optimized for first-time setup. Requires a git repository to be
    initialized.
"""

import logging
from collections.abc import Callable
from typing import Any

from pyrig.dev.cli.subcommands import mkroot, mktests
from pyrig.dev.management.package_manager import PackageManager
from pyrig.dev.management.pre_committer import (
    PreCommitter,
)
from pyrig.dev.management.project_tester import ProjectTester
from pyrig.dev.management.pyrigger import Pyrigger
from pyrig.dev.management.version_controller import VersionController
from pyrig.src.processes import Args
from pyrig.src.string_ import make_name_from_obj

logger = logging.getLogger(__name__)


def adding_dev_dependencies() -> Args:
    """Get args to install development dependencies (Step 1).

    Returns Args for adding pyrig's standard dev dependencies to pyproject.toml
    via `uv add --group dev`.

    Returns:
        Args object for adding dev dependencies.
    """
    return PackageManager.L.get_add_dev_dependencies_args(
        *Pyrigger.L.get_dev_dependencies()
    )


def creating_priority_config_files() -> Args:
    """Get args to create essential configuration files (Step 3).

    Returns Args for creating high-priority config files (pyproject.toml,
    .gitignore, LICENSE) that other initialization steps depend on via
    `pyrig mkroot --priority`.

    Returns:
        Args object for creating priority config files.
    """
    # local imports to avoid failure on init when dev deps are not installed yet.
    return Pyrigger.L.get_cmd_args("--priority", cmd=mkroot)


def syncing_venv() -> Args:
    """Get args to sync virtual environment with dependencies (Steps 2 & 4).

    Returns Args for installing all dependencies from pyproject.toml via
    `uv sync`. Run twice during initialization: after adding dev dependencies
    and after creating priority config files.

    Returns:
        Args object for syncing the virtual environment.
    """
    return PackageManager.L.get_install_dependencies_args()


def creating_project_root() -> Args:
    """Get args to create complete project structure and config files (Step 5).

    Returns Args for generating all remaining configuration files and directory
    structure via `pyrig mkroot`.

    Returns:
        Args object for creating the project root.
    """
    return Pyrigger.L.get_cmd_args(cmd=mkroot)


def creating_test_files() -> Args:
    """Get args to generate test skeleton files for all source code (Step 6).

    Returns Args for creating test files mirroring the source package structure
    with NotImplementedError placeholders via `pyrig mktests`.

    Returns:
        Args object for creating test files.
    """
    return Pyrigger.L.get_cmd_args(cmd=mktests)


def install_pre_commit_hooks() -> Args:
    """Get args to install pre-commit hooks (Step 7).

    Returns Args for installing pre-commit hooks into the git repository via
    `pre-commit install`.

    Returns:
        Args object for installing pre-commit hooks.
    """
    return PreCommitter.L.get_install_args()


def add_all_files_to_version_control() -> Args:
    """Get args to add all files to version control (Step 8).

    Returns Args for staging all files for commit via `git add .`.

    Returns:
        Args object for adding all files to version control.
    """
    return VersionController.L.get_add_all_args()


def running_pre_commit_hooks() -> Args:
    """Get args to run pre-commit hooks on all files (Step 9).

    Returns Args for running formatters/linters on all files to ensure the
    codebase follows style guidelines via `pre-commit run --all-files`.

    Returns:
        Args object for running pre-commit hooks.
    """
    return PreCommitter.L.get_run_all_files_args()


def running_tests() -> Args:
    """Get args to run the complete test suite (Step 10).

    Returns Args for validating that all generated code is syntactically correct
    and the project is properly configured via `pytest`.

    Returns:
        Args object for running tests.
    """
    return ProjectTester.L.get_test_args()


def committing_initial_changes() -> Args:
    """Get args to create initial git commit with all changes (Step 11).

    Returns Args for committing all configuration files, test skeletons, and
    formatting changes with the message "pyrig: Initial commit".

    Returns:
        Args object for committing initial changes.
    """
    # changes were added by the run pre-commit hooks step
    return VersionController.L.get_commit_no_verify_args(
        msg=f"{Pyrigger.name()}: Initial commit"
    )


SETUP_STEPS: list[Callable[..., Any]] = [
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
    are executed in order with progress logging. If any step fails, the process
    stops immediately.

    Note:
        This function should be run once when setting up a new project.
        Requires a git repository to be initialized.
    """
    logger.info("Initializing project")
    for step in SETUP_STEPS:
        step_name = make_name_from_obj(step, join_on=" ")
        logger.info(step_name)
        PackageManager.L.get_run_args(*step()).run()
    logger.info("Initialization complete!")
