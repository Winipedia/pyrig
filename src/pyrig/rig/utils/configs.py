"""Factory helpers for constructing config-file instances."""

from pyrig.rig import resources
from pyrig.rig.configs.base.init import InitConfigFile


def resources_init_config_file() -> InitConfigFile:
    """Build the ``InitConfigFile`` for the project's resources package.

    Dynamically generates an :class:`InitConfigFile` subclass bound to
    ``pyrig.rig.resources``, which manages the ``__init__.py`` of the target
    project's ``rig/resources`` package.

    Returns:
        An ``InitConfigFile`` instance for the ``rig/resources`` package
        ``__init__.py``.
    """
    return InitConfigFile.generate_subclass(resources)()
