"""Project structure and configuration file creation.

Generates all configuration files and directory structure by discovering
and validating `ConfigFile` subclasses.
"""

from pyrig.rig.configs.base.config_file import ConfigFile


def make_project_root() -> None:
    """Create project configuration files and directory structure.

    Discovers and validates all `ConfigFile` subclasses to create the complete
    project structure.
    """
    ConfigFile.validate_all_subclasses()
