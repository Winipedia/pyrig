"""Project initialization orchestration.

This module provides the main initialization flow for pyrig projects.
The `init()` function runs a series of setup steps to fully configure
a new project, including:

1. Adding dev dependencies (installs pyrig-dev package)
2. Syncing venv (installs all dependencies)
3. Creating priority config files (pyproject.toml, .gitignore, LICENSE, etc.)
4. Syncing venv (ensures new configs are applied)
5. Creating project root (generates all config files and directory structure)
6. Creating test files (generates test skeletons for all code)
7. Running pre-commit hooks (formats and lints all code)
8. Running tests (validates everything works)
9. Committing initial changes (creates initial git commit)

The initialization process is idempotent and can be re-run safely.

Example:
    Run from command line:
        $ uv run pyrig init

    Or programmatically:
        >>> from pyrig.src.project.init import init
        >>> init()
"""

import logging
from collections.abc import Callable
from typing import Any

import pyrig
from pyrig.dev.cli.subcommands import mkroot, mktests
from pyrig.dev.utils.consts import STANDARD_DEV_DEPS
from pyrig.src.project.mgt import (
    DependencyManager,
    PreCommit,
    Pyrig,
    TestRunner,
    VersionControl,
)
from pyrig.src.string import make_name_from_obj

logger = logging.getLogger(__name__)


def adding_dev_dependencies() -> None:
    """Install development dependencies.

    This installs the dev dependencies listed in pyproject.toml.
    """
    args = DependencyManager.get_add_dev_dependencies_args(*STANDARD_DEV_DEPS)
    args.run()


def creating_priority_config_files() -> None:
    """Create priority config files.

    This creates the priority config files that are required for
    the other setup steps.
    """
    # local imports to avoid failure on init when dev deps are not installed yet.
    args = Pyrig.get_cmd_args(mkroot, "--priority")
    args.run()


def syncing_venv() -> None:
    """Sync the virtual environment.

    This installs the dependencies listed in pyproject.toml.
    """
    args = DependencyManager.get_install_dependencies_args()
    args.run()


def creating_project_root() -> None:
    """Execute the create-root CLI command via subprocess.

    Invokes `uv run pyrig create-root` to generate all config files
    and the project directory structure.
    """
    args = Pyrig.get_cmd_args(mkroot)
    args.run()


def creating_test_files() -> None:
    """Execute the create-tests CLI command via subprocess.

    Invokes `uv run pyrig create-tests` to generate test skeleton
    files that mirror the source code structure.
    """
    args = Pyrig.get_cmd_args(mktests)
    args.run()


def running_pre_commit_hooks() -> None:
    """Run all pre-commit hooks.

    This runs all pre-commit hooks to ensure the codebase is
    in a clean, linted, and formatted state.
    """
    # install pre-commit hooks
    PreCommit.get_install_args().run()
    # add all files to git
    VersionControl.get_add_all_args().run()
    # run pre-commit hooks
    PreCommit.get_run_all_files_args().run()


def running_tests() -> None:
    """Run the test suite.

    This executes the test suite to verify that everything is
    working correctly after initialization.
    """
    args = TestRunner.get_run_tests_args()
    args.run()


def committing_initial_changes() -> None:
    """Commit all initial changes.

    This commits all changes made during initialization in a single commit.
    """
    # changes were added by the run pre-commit hooks step
    args = VersionControl.get_commit_no_verify_args(f"{pyrig.__name__}: Initial commit")
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
    """Initialize a pyrig project by running all setup steps.

    Executes each step in `SETUP_STEPS` sequentially, logging progress.
    This is the main entry point for the `pyrig init` command.

    The steps include:
        1. Adding dev dependencies (installs pyrig-dev package)
        2. Syncing venv (installs all dependencies)
        3. Creating priority config files (pyproject.toml, .gitignore, LICENSE, etc.)
        4. Syncing venv (ensures new configs are applied)
        5. Creating project root (generates all config files and directory structure)
        6. Creating test files (generates test skeletons for all code)
        7. Running pre-commit hooks (formats and lints all code)
        8. Running tests (validates everything works)
        9. Committing initial changes (creates initial git commit)
    """
    # for init set log level to info
    logging.basicConfig(level=logging.INFO)

    for step in SETUP_STEPS:
        step_name = make_name_from_obj(step, join_on=" ")
        logger.info(step_name)
        step()
    logger.info("Setup complete!")
