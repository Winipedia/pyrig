"""CLI command implementation for scaffolding the project resources package."""

from pyrig.rig import resources
from pyrig.rig.configs.base.init import InitConfigFile


def make_resources() -> None:
    """Scaffold the resources package ``__init__.py`` for the active project.

    Dynamically generates an ``InitConfigFile`` subclass bound to
    ``pyrig.rig.resources``, then validates it. If the file does not exist it
    is created with the correct content; if it already exists but is incorrect
    it is repaired.
    """
    # create the file if not existent yet
    config_file = InitConfigFile.generate_subclass(resources)()
    config_file.validate()
