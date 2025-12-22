"""Configuration management for YAML files.

This module provides the YamlConfigFile class for managing YAML configuration files.
"""

from typing import Any

import yaml

from pyrig.dev.configs.base.base import ConfigFile


class YamlConfigFile(ConfigFile):
    """Abstract base class for YAML configuration files.

    Provides YAML-specific load and dump implementations using PyYAML.
    """

    @classmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load and parse the YAML configuration file.

        Returns:
            The parsed YAML content as a dict or list.
        """
        return yaml.safe_load(cls.get_path().read_text(encoding="utf-8")) or {}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to the YAML file.

        Args:
            config: The configuration to write.
        """
        with cls.get_path().open("w") as f:
            yaml.safe_dump(config, f, sort_keys=False)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the YAML file extension.

        Returns:
            The string "yaml".
        """
        return "yaml"
