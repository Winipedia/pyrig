"""Project structure and configuration file creation.

Generates all configuration files and directory structure by discovering
and initializing ConfigFile subclasses.
"""

import logging

from pyrig.dev.configs.base.base import ConfigFile

logger = logging.getLogger(__name__)


def make_project_root(*, priority: bool = False) -> None:
    """Create project configuration files and directory structure.

    Discovers and initializes all ConfigFile subclasses to create the complete
    project structure.

    Args:
        priority: If True, only creates high-priority config files (e.g.,
            LICENSE, pyproject.toml). If False, creates all config files.
    """
    logger.info("Creating project root")
    if priority:
        ConfigFile.init_priority_subclasses()
        return
    ConfigFile.init_all_subclasses()
    logger.info("Project root creation complete")
