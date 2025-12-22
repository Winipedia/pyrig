"""Configuration management for JSON files.

This module provides the JsonConfigFile class for managing JSON configuration files.
"""

import json
from typing import Any

from pyrig.dev.configs.base.base import ConfigFile


class JsonConfigFile(ConfigFile):
    """Abstract base class for JSON configuration files.

    Provides JSON-specific load and dump implementations using PyYAML.
    """

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load and parse the JSON configuration file.

        Returns:
            The parsed JSON content as a dict or list.
        """
        path = cls.get_path()
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return data

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to the JSON file.

        Args:
            config: The configuration to write.
        """
        with cls.get_path().open("w") as f:
            json.dump(config, f, indent=4)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the JSON file extension.

        Returns:
            The string "json".
        """
        return "json"
