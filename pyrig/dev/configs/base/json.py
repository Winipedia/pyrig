"""JSON configuration file management.

Provides JsonConfigFile base class for JSON files using Python's built-in json module
with 4-space indentation.

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.dev.configs.base.json import JsonConfigFile
    >>>
    >>> class PackageJsonFile(JsonConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path()
    ...
    ...     @classmethod
    ...     def get_configs(cls) -> dict[str, Any]:
    ...         return {"name": "my-package", "version": "1.0.0"}
"""

import json
from typing import Any

from pyrig.dev.configs.base.base import ConfigFile


class JsonConfigFile(ConfigFile[dict[str, Any] | list[Any]]):
    """Base class for JSON configuration files.

    Uses Python's json module with 4-space indentation.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the JSON file
        - `get_configs`: Expected JSON configuration structure

    Example:
        >>> class MyConfigFile(JsonConfigFile):
        ...     @classmethod
        ...     def get_parent_path(cls) -> Path:
        ...         return Path()
        ...
        ...     @classmethod
        ...     def get_configs(cls) -> dict[str, Any]:
        ...         return {"setting": "value", "nested": {"key": "value"}}
    """

    @classmethod
    def _load(cls) -> dict[str, Any] | list[Any]:
        """Load and parse the JSON file.

        Returns:
            Parsed JSON content as dict.
        """
        path = cls.get_path()
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return data

    @classmethod
    def _dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to JSON file with 4-space indentation.

        Args:
            config: Configuration dict to write.
        """
        with cls.get_path().open("w") as f:
            json.dump(config, f, indent=4)

    @classmethod
    def get_file_extension(cls) -> str:
        """Return "json"."""
        return "json"
