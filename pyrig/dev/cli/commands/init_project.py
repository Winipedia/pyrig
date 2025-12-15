"""Project initialization orchestration.

This module provides the main initialization flow for pyrig projects.
The `init()` function runs a series of setup steps to fully configure
a new project, including:

1. Writing priority config files (pyproject.toml with dev dependencies)
2. Installing dependencies with uv
3. Creating project structure (source and test directories)
4. Running pre-commit hooks for initial formatting
5. Running tests to verify setup
6. Re-installing to activate CLI entry points

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
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.mgt import PROJECT_MGT, get_pyrig_cli_cmd_args
from pyrig.src.string import make_name_from_obj

logger = logging.getLogger(__name__)


STANDARD_DEV_DEPS: list[str] = ["pyrig-dev"]


def adding_dev_dependencies() -> None:
    """Install development dependencies.

    This installs the dev dependencies listed in pyproject.toml.
    """
    run_subprocess([PROJECT_MGT, "add", "--group", "dev", *STANDARD_DEV_DEPS])


def creating_priority_config_files() -> None:
    """Create priority config files.

    This creates the priority config files that are required for
    the other setup steps.
    """
    from pyrig.dev.configs.base.base import ConfigFile  # noqa: PLC0415

    ConfigFile.init_priority_config_files()


def syncing_venv() -> None:
    """Sync the virtual environment.

    This installs the dependencies listed in pyproject.toml.
    """
    run_subprocess([PROJECT_MGT, "sync"])


def creating_project_root() -> None:
    """Execute the create-root CLI command via subprocess.

    Invokes `uv run pyrig create-root` to generate all config files
    and the project directory structure.
    """
    from pyrig.dev.cli.subcommands import mkroot  # noqa: PLC0415

    run_subprocess(get_pyrig_cli_cmd_args(mkroot))


def creating_test_files() -> None:
    """Execute the create-tests CLI command via subprocess.

    Invokes `uv run pyrig create-tests` to generate test skeleton
    files that mirror the source code structure.
    """
    from pyrig.dev.cli.subcommands import mktests  # noqa: PLC0415

    run_subprocess(get_pyrig_cli_cmd_args(mktests))


def running_pre_commit_hooks() -> None:
    """Run all pre-commit hooks.

    This runs all pre-commit hooks to ensure the codebase is
    in a clean, linted, and formatted state.
    """
    from pyrig.dev.configs.git.pre_commit import (  # noqa: PLC0415
        PreCommitConfigConfigFile,
    )

    PreCommitConfigConfigFile.run_hooks(add_before_commit=True)


def running_tests() -> None:
    """Run the test suite.

    This executes the test suite to verify that everything is
    working correctly after initialization.
    """
    from pyrig.dev.configs.testing.conftest import ConftestConfigFile  # noqa: PLC0415

    ConftestConfigFile.run_tests()


def committing_initial_changes() -> None:
    """Commit all initial changes.

    This commits all changes made during initialization in a single commit.
    """
    # changes were added by the run pre-commit hooks step
    run_subprocess(
        ["git", "commit", "--no-verify", "-m", f"{pyrig.__name__}: Initial commit"]
    )


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
        1. Write priority config files (pyproject.toml)
        2. Install dependencies
        3. Update dependencies to latest
        4. Create project structure
        5. Generate test skeletons
        6. Run pre-commit hooks
        7. Run tests
        8. Re-install to activate CLI
    """
    # for init set log level to info
    logging.basicConfig(level=logging.INFO)

    for step in SETUP_STEPS:
        step_name = make_name_from_obj(step, join_on=" ")
        logger.info(step_name)
        step()
    logger.info("Setup complete!")
