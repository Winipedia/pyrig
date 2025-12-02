"""Pyrigs init script.

This script inits the project by calling all setup steps.
"""

import logging
from collections.abc import Callable
from typing import Any

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
    """Run create root."""
    from pyrig.dev.cli.subcommands import create_root  # noqa: PLC0415

    run_subprocess(get_project_mgt_run_pyrig_cli_cmd_args(create_root))


def run_create_tests() -> None:
    """Run create tests."""
    from pyrig.dev.cli.subcommands import create_tests  # noqa: PLC0415

    run_subprocess(get_project_mgt_run_pyrig_cli_cmd_args(create_tests))


SETUP_STEPS: list[Callable[..., Any]] = [
    ConfigFile.init_priority_config_files,  # write dev deps to pyproject.toml
    PyprojectConfigFile.install_dependencies,  # to install dev deps
    PyprojectConfigFile.update_dependencies,  # to update dev deps
    run_create_root,
    run_create_tests,
    PreCommitConfigConfigFile.run_hooks,
    ConftestConfigFile.run_tests,
    PyprojectConfigFile.install_dependencies,  # to activate cli
]


def init() -> None:
    """Set up the project."""
    for step in SETUP_STEPS:
        logger.info("Running setup step: %s", step.__name__)
        step()
    logger.info("Setup complete!")
