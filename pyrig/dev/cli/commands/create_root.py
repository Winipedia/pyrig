"""Project structure creation utilities.

This module provides the `create_root` function which generates all
configuration files and directory structure for a pyrig project.
It delegates to the ConfigFile system to discover and initialize
all registered config file types.
"""

import logging

from pyrig.dev.configs.base.base import ConfigFile

logger = logging.getLogger(__name__)


def make_project_root(*, priority: bool = False) -> None:
    """Create all configuration files and project structure.

    Discovers all ConfigFile subclasses and initializes each one,
    creating the complete project structure including:
        - pyproject.toml
        - GitHub workflows
        - Pre-commit configuration
        - Ruff/mypy configuration
        - Source and test directory structure

    This is the implementation for the `pyrig create-root` command.
    """
    logger.info("Creating project root")
    if priority:
        ConfigFile.init_priority_subclasses()
        return
    ConfigFile.init_all_subclasses()
    logger.info("Project root creation complete")
