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
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.git.pre_commit import PreCommitConfigConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.configs.testing.conftest import ConftestConfigFile
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.mgt import (
    get_project_mgt_run_pyrig_cli_cmd_args,
)

logger = logging.getLogger(__name__)


def run_create_root() -> None:
    """Execute the create-root CLI command via subprocess.

    Invokes `uv run pyrig create-root` to generate all config files
    and the project directory structure.
    """
    from pyrig.dev.cli.subcommands import create_root  # noqa: PLC0415

    run_subprocess(get_project_mgt_run_pyrig_cli_cmd_args(create_root))


def run_create_tests() -> None:
    """Execute the create-tests CLI command via subprocess.

    Invokes `uv run pyrig create-tests` to generate test skeleton
    files that mirror the source code structure.
    """
    from pyrig.dev.cli.subcommands import create_tests  # noqa: PLC0415

    run_subprocess(get_project_mgt_run_pyrig_cli_cmd_args(create_tests))


def commit_initial_changes() -> None:
    """Commit all initial changes.

    This commits all changes made during initialization in a single commit.
    """
    # changes were added by the run pre-commit hooks step
    run_subprocess(
        ["git", "commit", "--no-verify", "-m", f"{pyrig.__name__}: Initial commit"]
    )


SETUP_STEPS: list[Callable[..., Any]] = [
    ConfigFile.init_priority_config_files,  # write dev deps to pyproject.toml
    PyprojectConfigFile.install_dependencies,  # to install dev deps
    PyprojectConfigFile.update_dependencies,  # to update dev deps
    run_create_root,
    run_create_tests,
    PreCommitConfigConfigFile.run_hooks,
    ConftestConfigFile.run_tests,
    PyprojectConfigFile.install_dependencies,  # to activate cli
    commit_initial_changes,
]
"""Ordered list of setup steps executed during project initialization."""


def init() -> None:
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
        logger.info("Running setup step: %s", step.__name__)
        step()
    logger.info("Setup complete!")
