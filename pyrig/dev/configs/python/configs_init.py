"""Configuration for the {package_name}/dev/configs/__init__.py file.

This module provides the ConfigsInitConfigFile class for creating the
{package_name}/dev/configs/__init__.py file that mirrors pyrig's configs
package structure.

The generated file:
    - Copies the docstring from pyrig.dev.configs
    - Provides a place for custom ConfigFile subclasses
    - Enables automatic discovery of ConfigFile subclasses
    - Has high priority (10) to be created before other config files

All ConfigFile subclasses in the generated package are automatically
discovered and can be used to manage project configuration files.

See Also:
    pyrig.dev.configs
        Source module for the docstring
    pyrig.dev.configs.base.base.ConfigFile
        Base class for configuration file managers
"""

from types import ModuleType

from pyrig.dev import configs
from pyrig.dev.configs.base.init import InitConfigFile


class ConfigsInitConfigFile(InitConfigFile):
    '''Configuration file manager for {package_name}/dev/configs/__init__.py.

    Generates a {package_name}/dev/configs/__init__.py file with pyrig's
    configs module docstring, providing a starting point for custom ConfigFile
    subclasses.

    The generated file:
        - Contains only the docstring from pyrig.dev.configs
        - Provides a place for project-specific config file managers
        - Enables automatic ConfigFile discovery
        - Has priority 10 to be created before other config files

    Use Cases:
        - Define custom configuration file managers
        - Create project-specific config file templates
        - Extend pyrig's configuration management
        - Organize config-related code

    Examples:
        Generate {package_name}/dev/configs/__init__.py::

            from pyrig.dev.configs.python.configs_init import (
                ConfigsInitConfigFile,
            )

            # Creates {package_name}/dev/configs/__init__.py
            ConfigsInitConfigFile()

        Add custom config files to the generated package::

            # In {package_name}/dev/configs/my_config.py
            from pyrig.dev.configs.base.base import ConfigFile

            class MyConfigFile(ConfigFile):
                """Custom configuration file manager."""
                pass

    See Also:
        pyrig.dev.configs
            Source module for the docstring
        pyrig.dev.configs.base.base.ConfigFile
            Base class for configuration file managers
    '''

    @classmethod
    def get_priority(cls) -> float:
        """Get the priority for this config file.

        Higher priority files are created first. This file has priority 10 to
        ensure it's created before other config files that may depend on it.

        Returns:
            float: Priority value of 10.0 (higher than default).

        Note:
            This ensures the configs directory exists before other config
            files try to use it.
        """
        return 10

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy docstring from.

        Returns:
            ModuleType: The pyrig.dev.configs module.

        Note:
            Only the docstring is copied; no code is included in the
            generated file.
        """
        return configs
