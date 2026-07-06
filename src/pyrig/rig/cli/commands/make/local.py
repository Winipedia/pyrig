"""Creation logic for version-control-ignored local development files."""

from pyrig.rig.configs.base.config_file import ConfigFile


def make_local_files() -> None:
    """Validate every version-control-ignored config file."""
    ConfigFile.validate_subclasses(ConfigFile.version_control_ignored_subclasses())
