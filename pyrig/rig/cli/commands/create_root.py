"""Project structure and configuration file creation.

Generates all configuration files and directory structure by discovering
and validating `ConfigFile` subclasses.
"""

import logging

from pyrig.rig.configs.base.base import ConfigFile

logger = logging.getLogger(__name__)


def make_project_root() -> None:
    """Create project configuration files and directory structure.

    Discovers and validates all `ConfigFile` subclasses to create the complete
    project structure.
    """
    logger.info("Creating project root")
    ConfigFile.validate_all_subclasses()
    logger.info("Project root creation complete")
