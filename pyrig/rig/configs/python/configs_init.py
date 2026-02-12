"""Configuration for {package_name}/rig/configs/__init__.py.

Generates {package_name}/rig/configs/__init__.py with pyrig.rig.configs docstring.
Has priority 10 to be created before other config files. Enables automatic
discovery of custom ConfigFile subclasses.

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

    Generates __init__.py with pyrig.rig.configs docstring for custom ConfigFile
    subclasses. Has priority 10 to be created before other config files.

    Examples:
        Generate {package_name}/rig/configs/__init__.py::

            ConfigsInitConfigFile()

    See Also:
        pyrig.rig.configs
        pyrig.rig.configs.base.base.ConfigFile
    """

    @classmethod
    def priority(cls) -> float:
        """Get the priority for this config file.

        Returns:
            float: 10.0 (ensures configs directory exists before other files use it).
        """
        return Priority.LOW

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: pyrig.rig.configs module.

        Note:
            Only docstring is copied, no code.
        """
        return configs
