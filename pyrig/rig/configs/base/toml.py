"""TOML configuration file management.

Provides TomlConfigFile base class using tomlkit for parsing and writing with
formatting preservation. Arrays formatted as multiline for readability.

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.rig.configs.base.toml import TomlConfigFile
    >>>
    >>> class MyConfigFile(TomlConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...     def parent_path(self) -> Path:
    ...
    ...
    ...     def _configs(self) -> dict[str, Any]:
    ...         return {"tool": {"myapp": {"dependencies": ["dep1", "dep2"]}}}
"""

from typing import Any

import tomlkit
from tomlkit.items import Table

from pyrig.rig.configs.base.dict_cf import DictConfigFile


class TomlConfigFile(DictConfigFile):
    """Base class for TOML configuration files.

    Uses tomlkit for parsing/writing with formatting preservation. Arrays formatted
    as multiline, key order preserved.

    Subclasses must implement:
        - `parent_path`: Directory containing the TOML file
        - `_configs`: Expected TOML configuration structure

    Example:
        >>> class MyConfigFile(TomlConfigFile):
        ...
        ...     def parent_path(self) -> Path:
        ...     def parent_path(self) -> Path:
        ...
        ...
        ...     def _configs(self) -> dict[str, Any]:
        ...         return {"tool": {"myapp": {"version": "1.0.0"}}}
    """

    def _load(self) -> dict[str, Any]:
        """Load and parse TOML file using tomlkit.parse.

        Returns:
            Parsed TOML as `tomlkit.TOMLDocument` (dict-like with formatting info).
        """
        return tomlkit.parse(self.path().read_text(encoding="utf-8"))

    def _dump(self, config: dict[str, Any]) -> None:
        """Validate and write configuration to TOML file.

        Args:
            config: Configuration dict to write.

        Raises:
            TypeError: If config is not a dict (TOML requires top-level table).
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to toml file."
            raise TypeError(msg)
        self.pretty_dump(config)

    def prettify_value(self, value: Any) -> Any:
        """Recursively prettify a value for TOML output.

        Lists of dicts become arrays of tables (``[[section]]`` syntax).
        Other lists become multiline arrays. Dicts become tables with recursively
        prettified values. Scalars are returned as-is.

        Args:
            value: Value to prettify (list, dict, or scalar).

        Returns:
            Prettified tomlkit value.
        """
        if isinstance(value, list):
            if value and all(isinstance(item, dict) for item in value):
                aot = tomlkit.aot()
                for item in value:
                    aot.append(self.prettify_dict(item))
                return aot
            arr = tomlkit.array().multiline(multiline=True)
            for item in value:
                arr.append(self.prettify_value(item))
            return arr
        if isinstance(value, dict):
            return self.prettify_dict(value)
        return value

    def prettify_dict(self, config: dict[str, Any]) -> Table:
        """Convert dict to tomlkit table with multiline arrays.

        Recursively processes config: lists of dicts become arrays of tables
        (``[[section]]`` syntax), other lists become multiline arrays, dicts become
        nested tables, scalars added as-is.

        Args:
            config: Configuration dict to prettify.

        Returns:
            tomlkit.table() with formatted arrays.
        """
        t = tomlkit.table()
        for k, v in config.items():
            t.add(k, self.prettify_value(v))
        return t

    def pretty_dump(self, config: dict[str, Any]) -> None:
        """Write configuration to TOML with pretty formatting.

        Convert config to prettified tomlkit table via `prettify_dict()`, then write
        with multiline arrays and preserved key order.

        Args:
            config: Configuration dict to write.
        """
        # turn all lists into multiline arrays
        config = self.prettify_dict(config)
        with self.path().open("w") as f:
            tomlkit.dump(config, f, sort_keys=False)

    def extension(self) -> str:
        """Return "toml"."""
        return "toml"

    def extension(self) -> str: