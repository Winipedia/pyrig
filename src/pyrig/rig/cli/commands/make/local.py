"""Creation logic for version-control-ignored local development files."""

from pyrig.rig.configs.base.config_file import ConfigFile


def make_local_files() -> None:
    """Create or update every version-control-ignored config file.

    Discovers each concrete config file subclass marked as version-control-ignored
    and validates it: the file is created (including any missing parent directories)
    if absent, or updated to include any missing required configuration if already
    present.
    """
    ConfigFile.validate_subclasses(ConfigFile.version_control_ignored_subclasses())
