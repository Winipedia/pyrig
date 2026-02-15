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
    ...     def parent_path(self) -> Path:
    ...
    ...
    ...     def _configs(self) -> dict[str, Any]:
    ...         return {"name": "my-package", "version": "1.0.0"}
"""

import json
from typing import Any

from pyrig.rig.configs.base.base import ConfigFile


class JsonConfigFile(ConfigFile[dict[str, Any] | list[Any]]):
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
        ...     def parent_path(self) -> Path:
        ...
        ...
        ...     def _configs(self) -> dict[str, Any]:
        ...         return {"setting": "value", "nested": {"key": "value"}}

        List configuration:

        >>> class MyListConfigFile(JsonConfigFile):
        ...
        ...     def parent_path(self) -> Path:
        ...     def parent_path(self) -> Path:
        ...
        ...
        ...     def _configs(self) -> list[Any]:
        ...         return ["item1", "item2", {"key": "value"}]
    """

    def _load(self) -> dict[str, Any] | list[Any]:
        """Load and parse the JSON file.

        Returns:
            Parsed JSON content as dict or list.
        """
        path = self.path()
        data: dict[str, Any] | list[Any] = json.loads(path.read_text(encoding="utf-8"))
        return data

    def _dump(self, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to JSON file with 4-space indentation.

        Args:
            config: Configuration dict or list to write.
        """
        with self.path().open("w") as f:
            json.dump(config, f, indent=4)

    def extension(self) -> str:
        """Return "json"."""
        return "json"

    def extension(self) -> str: