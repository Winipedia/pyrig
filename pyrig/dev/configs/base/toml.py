"""TOML configuration file management.

Provides TomlConfigFile base class using tomlkit for parsing and writing with
formatting preservation. Arrays formatted as multiline for readability.

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
    ...     def _get_configs(cls) -> dict[str, Any]:
    ...         return {"tool": {"myapp": {"dependencies": ["dep1", "dep2"]}}}
"""

from typing import Any

import tomlkit

from pyrig.dev.configs.base.dict_cf import DictConfigFile


class TomlConfigFile(DictConfigFile):
    """Base class for TOML configuration files.

    Uses tomlkit for parsing/writing with formatting preservation. Arrays formatted
    as multiline, key order preserved.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the TOML file
        - `_get_configs`: Expected TOML configuration structure

    Example:
        >>> class MyConfigFile(TomlConfigFile):
        ...     @classmethod
        ...     def get_parent_path(cls) -> Path:
        ...         return Path()
        ...
        ...     @classmethod
        ...     def _get_configs(cls) -> dict[str, Any]:
        ...         return {"tool": {"myapp": {"version": "1.0.0"}}}
    """

    @classmethod
    def _load(cls) -> dict[str, Any]:
        """Load and parse TOML file using tomlkit.parse.

        Returns:
            Parsed TOML as tomlkit.TOMLDocument (dict-like with formatting info).
        """
        return tomlkit.parse(cls.get_path().read_text(encoding="utf-8"))

    @classmethod
    def _dump(cls, config: dict[str, Any]) -> None:
        """Write configuration to TOML with pretty formatting.

        Args:
            config: Configuration dict to write.

        Raises:
            TypeError: If config is not a dict (TOML requires top-level table).
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to toml file."
            raise TypeError(msg)
        cls.pretty_dump(config)

    @classmethod
    def prettify_dict(cls, config: dict[str, Any]) -> dict[str, Any]:
        """Convert dict to tomlkit table with multiline arrays.

        Recursively processes config: lists become multiline arrays (inline tables
        for dict lists), dicts become nested tables, scalars added as-is.

        Args:
            config: Configuration dict to prettify.

        Returns:
            tomlkit.table() with formatted arrays.
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

        Converts config to prettified tomlkit table via prettify_dict(), then writes
        with multiline arrays and preserved key order.

        Args:
            config: Configuration dict to write.
        """
        # turn all lists into multiline arrays
        config = cls.prettify_dict(config)
        with cls.get_path().open("w") as f:
            tomlkit.dump(config, f, sort_keys=False)

    @classmethod
    def get_file_extension(cls) -> str:
        """Return "toml"."""
        return "toml"
