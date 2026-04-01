"""Helpers to scaffold the resources package."""

from pyrig.rig import resources
from pyrig.rig.configs.base.init import InitConfigFile


def make_resources() -> None:
    """Create the resources package if it doesn't exist yet."""
    # create the file if not existent yet
    config_file = InitConfigFile.generate_subclass(resources)()
    config_file.validate()
