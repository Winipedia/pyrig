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
from pyrig.src.project.create_root import create_root
from pyrig.src.testing.create_tests import create_tests

logger = logging.getLogger(__name__)


SETUP_STEPS: list[Callable[..., Any]] = [
    ConfigFile.init_priority_config_files,  # write dev deps to pyproject.toml
    PyprojectConfigFile.install_dependencies,  # to install dev deps
    PyprojectConfigFile.update_dependencies,  # to update dev deps
    create_root,
    create_tests,
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
