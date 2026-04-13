"""JSON configuration file management.

Provides JsonConfigFile base class for JSON files using Python's built-in json module
with 4-space indentation.

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.rig.configs.base.json import JsonConfigFile
    >>>
    >>> class PackageJsonFile(JsonConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...         return Path()
    ...
    ...
    ...     def _configs(self) -> ConfigDict:
    ...         return {"name": "my-package", "version": "1.0.0"}
"""

import json

from pyrig.core.string_ import read_text_utf8
from pyrig.core.types.config_file import ConfigDict
from pyrig.rig.configs.base.config_file import ConfigFile, ConfigT


class JsonConfigFile(ConfigFile[ConfigT]):
    """Base class for JSON configuration files.

    Uses Python's json module with 4-space indentation. Supports both dict and
    list as top-level structures.

    Subclasses must implement:
        - `parent_path`: Directory containing the JSON file
        - `_configs`: Expected JSON configuration structure

    Example:
        Dict configuration:

        >>> class MyConfigFile(JsonConfigFile):
        ...
        ...     def parent_path(self) -> Path:
        ...         return Path()
        ...
        ...
        ...     def _configs(self) -> ConfigDict:
        ...         return {"setting": "value", "nested": {"key": "value"}}

        List configuration:

        >>> class MyListConfigFile(JsonConfigFile):
        ...
        ...     def parent_path(self) -> Path:
        ...         return Path()
        ...
        ...
        ...     def _configs(self) -> ConfigList:
        ...         return ["item1", "item2", {"key": "value"}]
    """

    def _load(self) -> ConfigT:
        """Load and parse the JSON file.

        Returns:
            Parsed JSON content as dict or list.
        """
        path = self.path()
        data: ConfigT = json.loads(read_text_utf8(path))
        return data

    def _dump(self, config: ConfigT) -> None:
        """Write configuration to JSON file with 4-space indentation.

        Args:
            config: Configuration dict or list to write.
        """
        with self.path().open("w") as f:
            json.dump(config, f, indent=4)

    def extension(self) -> str:
        """Return "json"."""
        return "json"


class DictJsonConfigFile(JsonConfigFile[ConfigDict]):
    """JsonConfigFile subclass for dict-based JSON configurations."""
