"""Complete project initialization orchestration.

Transforms a basic Python project into a fully-configured, production-ready
pyrig project through a comprehensive 9-step automated sequence.

The initialization process executes steps in a specific order to ensure all
dependencies and configurations are properly established. Each step is
implemented as a separate function and executed sequentially. If any step
fails, the process stops immediately.

Initialization Steps:
    1. Adding dev dependencies (uv add --dev)
    2. Syncing venv (uv sync)
    3. Creating priority config files (pyproject.toml, .gitignore, LICENSE)
    4. Syncing venv again (apply new configs)
    5. Creating project root (all remaining config files)
    6. Creating test files (test skeletons for all source code)
    7. Running pre-commit hooks (install, stage, format/lint)
    8. Running tests (validate everything works)
    9. Committing initial changes (create initial git commit)

Note:
    This process is designed for initial setup, not repeated execution.
    Individual steps (mkroot, mktests) are idempotent, but the full sequence
    is optimized for first-time setup. Requires a git repository to be
    initialized.
"""

import logging
from collections.abc import Callable
from typing import Any

import pyrig
from pyrig.dev.cli.subcommands import mkroot, mktests
from pyrig.dev.management.package_manager import PackageManager
from pyrig.dev.management.pre_committer import (
    PreCommitter,
)
from pyrig.dev.management.project_tester import ProjectTester
from pyrig.dev.management.pyrigger import Pyrigger
from pyrig.dev.management.version_controller import VersionController
from pyrig.src.consts import STANDARD_DEV_DEPS
from pyrig.src.string import make_name_from_obj

logger = logging.getLogger(__name__)


def adding_dev_dependencies() -> None:
    """Install development dependencies (Step 1).

    Adds pyrig's standard dev dependencies to pyproject.toml via
    `uv add --dev`.
    """
    args = PackageManager.get_add_dev_dependencies_args(*STANDARD_DEV_DEPS)
    args.run()


def creating_priority_config_files() -> None:
    """Create essential configuration files (Step 3).

    Creates high-priority config files (pyproject.toml, .gitignore, LICENSE)
    that other initialization steps depend on via `uv run pyrig mkroot --priority`.
    """
    # local imports to avoid failure on init when dev deps are not installed yet.
    args = PackageManager.get_run_args(*Pyrigger.get_cmd_args(mkroot, "--priority"))
    args.run()


def syncing_venv() -> None:
    """Sync virtual environment with dependencies (Steps 2 & 4).

    Installs all dependencies from pyproject.toml via `uv sync`. Run twice
    during initialization: after adding dev dependencies and after creating
    priority config files.
    """
    args = PackageManager.get_install_dependencies_args()
    args.run()


def creating_project_root() -> None:
    """Create complete project structure and config files (Step 5).

    Generates all remaining configuration files and directory structure via
    `uv run pyrig mkroot`.
    """
    args = PackageManager.get_run_args(*Pyrigger.get_cmd_args(mkroot))
    args.run()


def creating_test_files() -> None:
    """Generate test skeleton files for all source code (Step 6).

    Creates test files mirroring the source package structure with
    NotImplementedError placeholders via `uv run pyrig mktests`.
    """
    args = PackageManager.get_run_args(*Pyrigger.get_cmd_args(mktests))
    args.run()


def running_pre_commit_hooks() -> None:
    """Install and run pre-commit hooks on all files (Step 7).

    Installs pre-commit hooks, stages all files, and runs formatters/linters
    to ensure the codebase follows style guidelines.
    """
    # install pre-commit hooks
    PackageManager.get_run_args(*PreCommitter.get_install_args()).run()
    # add all files to git
    VersionController.get_add_all_args().run()
    # run pre-commit hooks
    PackageManager.get_run_args(*PreCommitter.get_run_all_files_args()).run()


def running_tests() -> None:
    """Run the complete test suite (Step 8).

    Validates that all generated code is syntactically correct and the project
    is properly configured via `pytest`.
    """
    args = PackageManager.get_run_args(*ProjectTester.get_args())
    args.run()


def committing_initial_changes() -> None:
    """Create initial git commit with all changes (Step 9).

    Commits all configuration files, test skeletons, and formatting changes
    with the message "pyrig: Initial commit".
    """
    # changes were added by the run pre-commit hooks step
    args = VersionController.get_commit_no_verify_args(
        msg=f"{pyrig.__name__}: Initial commit"
    )
    args.run()


SETUP_STEPS: list[Callable[..., Any]] = [
    adding_dev_dependencies,
    syncing_venv,
    creating_priority_config_files,
    syncing_venv,
    creating_project_root,
    creating_test_files,
    running_pre_commit_hooks,
    running_tests,
    committing_initial_changes,
]


def init_project() -> None:
    """Initialize a pyrig project by running all setup steps sequentially.

    Executes the complete 9-step initialization sequence to transform a basic
    Python project into a fully-configured, production-ready pyrig project.

    Each step is executed in order with progress logging. If any step fails,
    the process stops immediately.

    Note:
        This function should be run once when setting up a new project.
        Requires a git repository to be initialized.
    """
    logger.info("Initializing project")
    for step in SETUP_STEPS:
        step_name = make_name_from_obj(step, join_on=" ")
        logger.info(step_name)
        step()
    logger.info("Initialization complete!")
