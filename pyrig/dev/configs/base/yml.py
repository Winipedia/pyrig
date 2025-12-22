"""Configuration management for yml files.

This module provides the YmlConfigFile class for managing yml configuration files.
"""

from pyrig.dev.configs.base.yaml import YamlConfigFile


class YmlConfigFile(YamlConfigFile):
    """Abstract base class for yml configuration files.

    Provides yml-specific load and dump implementations using PyYAML.
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the yml file extension.

        Returns:
            The string "yml".
        """
        return "yml"
