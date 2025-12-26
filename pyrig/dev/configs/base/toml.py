"""Configuration management for TOML files.

This module provides the TomlConfigFile class for managing TOML configuration
files. It uses tomlkit for parsing and writing, which preserves formatting,
comments, and style from the original file.

The TOML implementation includes special formatting for arrays:
- Lists are converted to multiline arrays for readability
- Lists of dicts use inline table syntax
- Nested dicts are properly formatted as TOML tables

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.dev.configs.base.toml import TomlConfigFile
    >>>
    >>> class MyConfigFile(TomlConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path()
    ...
    ...     @classmethod
    ...     def get_configs(cls) -> dict[str, Any]:
    ...         return {
    ...             "tool": {
    ...                 "myapp": {
    ...                     "dependencies": ["dep1", "dep2"],
    ...                     "setting": "value"
    ...                 }
    ...             }
    ...         }
"""

from typing import Any

import tomlkit

from pyrig.dev.configs.base.base import ConfigFile


class TomlConfigFile(ConfigFile):
    """Abstract base class for TOML configuration files.

    Provides TOML-specific load and dump implementations using tomlkit,
    which preserves formatting, comments, and style from the original file.
    This is particularly important for files like pyproject.toml where
    maintaining readability is crucial.

    The class includes special formatting logic:
    - Arrays are formatted as multiline for readability
    - Lists of dicts use inline table syntax
    - Nested structures are properly indented
    - Original key order is preserved (no sorting)

    Subclasses must implement:
        - `get_parent_path`: Directory containing the TOML file
        - `get_configs`: Expected TOML configuration structure

    Example:
        >>> from pathlib import Path
        >>> from typing import Any
        >>> from pyrig.dev.configs.base.toml import TomlConfigFile
        >>>
        >>> class MyConfigFile(TomlConfigFile):
        ...     @classmethod
        ...     def get_parent_path(cls) -> Path:
        ...         return Path()
        ...
        ...     @classmethod
        ...     def get_configs(cls) -> dict[str, Any]:
        ...         return {
        ...             "tool": {
        ...                 "myapp": {
        ...                     "version": "1.0.0"
        ...                 }
        ...             }
        ...         }
    """

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load and parse the TOML configuration file.

        Returns:
            The parsed TOML content as a dict.
        """
        return tomlkit.parse(cls.get_path().read_text(encoding="utf-8"))

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to the TOML file.

        Args:
            config: The configuration dict to write.

        Raises:
            TypeError: If config is not a dict.
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to toml file."
            raise TypeError(msg)
        cls.pretty_dump(config)

    @classmethod
    def prettify_dict(cls, config: dict[str, Any]) -> dict[str, Any]:
        """Convert a dict to a tomlkit table with multiline arrays.

        Recursively processes the configuration dict to create a tomlkit table
        with proper formatting:
        - Lists are converted to multiline arrays
        - Lists of dicts use inline table syntax
        - Nested dicts are recursively prettified

        Args:
            config: The configuration dict to prettify.

        Returns:
            A tomlkit table with formatted arrays and proper structure.

        Example:
            >>> config = {
            ...     "dependencies": ["dep1", "dep2"],
            ...     "tool": {"setting": "value"}
            ... }
            >>> prettified = TomlConfigFile.prettify_dict(config)
            # Results in multiline array for dependencies
        """
        t = tomlkit.table()

        for key, value in config.items():
            if isinstance(value, list):
                # Check if all items are dicts - use inline tables for those
                if value and all(isinstance(item, dict) for item in value):
                    arr = tomlkit.array().multiline(multiline=True)
                    for item in value:
                        inline_table = tomlkit.inline_table()
                        inline_table.update(item)
                        arr.append(inline_table)
                    t.add(key, arr)
                else:
                    # For non-dict items, use multiline arrays
                    arr = tomlkit.array().multiline(multiline=True)
                    for item in value:
                        arr.append(item)
                    t.add(key, arr)

            elif isinstance(value, dict):
                t.add(key, cls.prettify_dict(value))

            else:
                t.add(key, value)

        return t

    @classmethod
    def pretty_dump(cls, config: dict[str, Any]) -> None:
        """Write configuration to TOML with pretty formatting.

        Converts the configuration dict to a prettified tomlkit table and
        writes it to the file. Lists are converted to multiline arrays for
        better readability, and key order is preserved.

        Args:
            config: The configuration dict to write.

        Note:
            This method uses `prettify_dict` to format arrays and nested
            structures before writing. The resulting TOML file is more
            readable than the default tomlkit output.
        """
        # turn all lists into multiline arrays
        config = cls.prettify_dict(config)
        with cls.get_path().open("w") as f:
            tomlkit.dump(config, f, sort_keys=False)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the TOML file extension.

        Returns:
            The string "toml".
        """
        return "toml"
