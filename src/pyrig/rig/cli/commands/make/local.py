"""Creation logic for version-control-ignored local development files."""

from pyrig.rig.configs.base.config_file import ConfigFile


def make_local_files() -> None:
    """Create all version-control-ignored config files.

    Discovers every concrete ``ConfigFile`` subclass whose
    ``version_control_ignored()`` returns ``True`` and calls ``validate()``
    on each one, creating the file (and any missing parent directories) if it
    does not already exist.
    """
    ConfigFile.validate_subclasses(ConfigFile.version_control_ignored_subclasses())
