"""Creation logic for version-control-ignored local development files."""

from pyrig.rig.configs.base.config_file import ConfigFile


def make_local_files() -> None:
    """Create or update every version-control-ignored config file.

    Discovers each concrete [ConfigFile][] subclass whose
    `version_control_ignored()` returns `True` and validates it, creating the
    file (and any missing parent directories) when absent or merging in any
    missing required configuration when it already exists.
    """
    ConfigFile.validate_subclasses(ConfigFile.version_control_ignored_subclasses())
