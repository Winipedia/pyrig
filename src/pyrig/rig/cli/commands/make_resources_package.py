"""CLI command implementation for scaffolding the project resources package."""

from pyrig.rig.utils.configs import resources_init_config_file


def make_resources_package() -> None:
    """Scaffold the resources package ``__init__.py`` for the active project.

    Dynamically generates an ``InitConfigFile`` subclass bound to
    ``pyrig.rig.resources``, then validates it. If the file does not exist it
    is created with the correct content; if it already exists with correct content,
    it is not modified.
    """
    resources_init_config_file().validate()
