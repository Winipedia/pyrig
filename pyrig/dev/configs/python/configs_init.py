"""Configuration for {package_name}/dev/configs/__init__.py.

Generates {package_name}/dev/configs/__init__.py with pyrig.dev.configs docstring.
Has priority 10 to be created before other config files. Enables automatic
discovery of custom ConfigFile subclasses.

See Also:
    pyrig.dev.configs
    pyrig.dev.configs.base.base.ConfigFile
"""

from types import ModuleType

from pyrig.dev import configs
from pyrig.dev.configs.base.init import InitConfigFile


class ConfigsInitConfigFile(InitConfigFile):
    """Manages {package_name}/dev/configs/__init__.py.

    Generates __init__.py with pyrig.dev.configs docstring for custom ConfigFile
    subclasses. Has priority 10 to be created before other config files.

    Examples:
        Generate {package_name}/dev/configs/__init__.py::

            ConfigsInitConfigFile()

    See Also:
        pyrig.dev.configs
        pyrig.dev.configs.base.base.ConfigFile
    """

    @classmethod
    def get_priority(cls) -> float:
        """Get the priority for this config file.

        Returns:
            float: 10.0 (ensures configs directory exists before other files use it).
        """
        return 10

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: pyrig.dev.configs module.

        Note:
            Only docstring is copied, no code.
        """
        return configs
