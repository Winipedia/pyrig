"""Configuration for {package_name}/rig/configs/__init__.py.

Generates {package_name}/rig/configs/__init__.py with the docstring copied from
pyrig.rig.configs. Has priority 10 to be created before other config files.

See Also:
    pyrig.rig.configs
    pyrig.rig.configs.base.base.ConfigFile
"""

from types import ModuleType

from pyrig.rig import configs
from pyrig.rig.configs.base.base import Priority
from pyrig.rig.configs.base.init import InitConfigFile


class ConfigsInitConfigFile(InitConfigFile):
    """Manages {package_name}/rig/configs/__init__.py.

    Generates __init__.py for the rig/configs package, copying the docstring
    from pyrig.rig.configs. Has priority 10 to be created before other config
    files.

    Examples:
        Generate {package_name}/rig/configs/__init__.py::

            ConfigsInitConfigFile.I.validate()

    See Also:
        pyrig.rig.configs
        pyrig.rig.configs.base.base.ConfigFile
    """

    def priority(self) -> float:
        """Get the priority for this config file.

        Returns:
            `Priority.LOW` (10), ensuring the configs directory exists before
            other config files use it.
        """
        return Priority.LOW

    def src_module(self) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            The `pyrig.rig.configs` module.

        Note:
            Only docstring is copied, no code.
        """
        return configs
