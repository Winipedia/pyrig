"""Implementation of the ``mkroot`` CLI command.

Provides the backend logic for generating and maintaining all project
configuration files and directory structure.
"""

from pyrig.rig.configs.base.config_file import ConfigFile


def make_project_root() -> None:
    """Create or update all project configuration files and directory structure.

    Discovers every concrete ``ConfigFile`` subclass registered across the
    project and its installed dependencies, then validates each one in priority
    order. Validation creates missing files and overwrites files whose content
    is out of date while leaving correct files untouched.

    Idempotent: safe to run multiple times with consistent results.

    Raises:
        RuntimeError: If any config file cannot be made correct after merging
            and writing its expected configuration.
    """
    ConfigFile.validate_all_subclasses()
