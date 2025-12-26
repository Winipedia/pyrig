"""Configuration management for JSON files.

This module provides the JsonConfigFile class for managing JSON configuration
files. It uses Python's built-in json module for parsing and writing.

JSON files are commonly used for:
- Package configuration (package.json for Node.js projects)
- VS Code settings (.vscode/settings.json)
- Build tool configuration
- API schemas and data files

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
    ...         return {
    ...             "name": "my-package",
    ...             "version": "1.0.0",
    ...             "scripts": {
    ...                 "test": "jest"
    ...             }
    ...         }
"""

import json
from typing import Any

from pyrig.dev.configs.base.base import ConfigFile


class JsonConfigFile(ConfigFile):
    """Abstract base class for JSON configuration files.

    Provides JSON-specific load and dump implementations using Python's
    built-in json module. JSON files are formatted with 4-space indentation
    for readability.

    The implementation:
    - Uses json.loads() for parsing (standard JSON parsing)
    - Uses json.dump() with indent=4 for writing (readable formatting)
    - Supports both dict and list as top-level structures
    - Handles nested structures automatically

    Subclasses must implement:
        - `get_parent_path`: Directory containing the JSON file
        - `get_configs`: Expected JSON configuration structure

    Example:
        >>> from pathlib import Path
        >>> from typing import Any
        >>> from pyrig.dev.configs.base.json import JsonConfigFile
        >>>
        >>> class MyConfigFile(JsonConfigFile):
        ...     @classmethod
        ...     def get_parent_path(cls) -> Path:
        ...         return Path()
        ...
        ...     @classmethod
        ...     def get_configs(cls) -> dict[str, Any]:
        ...         return {
        ...             "setting": "value",
        ...             "nested": {
        ...                 "key": "value"
        ...             }
        ...         }
    """

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load and parse the JSON configuration file.

        Uses Python's built-in json.loads() to parse the file content. The
        method reads the file as UTF-8 text and parses it as JSON.

        Returns:
            The parsed JSON content as a dict or list. The exact type depends
            on the top-level structure in the JSON file.

        Example:
            Load a JSON file::

                # config.json contains:
                # {
                #   "name": "myapp",
                #   "version": "1.0.0"
                # }

                config = MyJsonConfigFile.load()
                # Returns: {"name": "myapp", "version": "1.0.0"}

        Note:
            The return type annotation says dict[str, Any] but the actual
            return value could be a list if the JSON file has a top-level
            array. This is a limitation of the type system.
        """
        path = cls.get_path()
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        return data

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to the JSON file with 4-space indentation.

        Uses Python's built-in json.dump() with indent=4 to write the
        configuration. The resulting JSON file is formatted with 4-space
        indentation for readability.

        Args:
            config: The configuration to write. Can be a dict or list. Nested
                structures are supported.

        Example:
            Write a JSON file::

                config = {
                    "name": "myapp",
                    "version": "1.0.0",
                    "dependencies": {
                        "requests": "^2.28.0"
                    }
                }
                MyJsonConfigFile.dump(config)

                # Creates config.json:
                # {
                #     "name": "myapp",
                #     "version": "1.0.0",
                #     "dependencies": {
                #         "requests": "^2.28.0"
                #     }
                # }

        Note:
            The indent=4 parameter ensures the JSON is formatted with 4-space
            indentation, making it more readable than compact JSON.
        """
        with cls.get_path().open("w") as f:
            json.dump(config, f, indent=4)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the JSON file extension.

        Returns:
            The string "json" (without the leading dot).

        Example:
            For a class named PackageJsonConfigFile::

                get_filename() -> "package_json"
                get_file_extension() -> "json"
                get_path() -> Path("package.json")
        """
        return "json"
