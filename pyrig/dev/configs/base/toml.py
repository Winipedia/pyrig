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

        Uses tomlkit.parse() to read the file, which preserves formatting,
        comments, and style from the original file. This is important for
        maintaining readability in files like pyproject.toml.

        Returns:
            The parsed TOML content as a dict. Returns a tomlkit.TOMLDocument
            which behaves like a dict but preserves formatting information.

        Example:
            Load a TOML file::

                # pyproject.toml contains:
                # [tool.myapp]
                # version = "1.0.0"

                config = MyTomlConfigFile.load()
                # Returns: {"tool": {"myapp": {"version": "1.0.0"}}}
        """
        return tomlkit.parse(cls.get_path().read_text(encoding="utf-8"))

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write configuration to the TOML file with pretty formatting.

        Validates that the config is a dict (TOML requires a top-level table),
        then writes it using pretty_dump() which formats arrays as multiline
        for better readability.

        Args:
            config: The configuration dict to write. Must be a dict, not a list,
                since TOML requires a top-level table.

        Raises:
            TypeError: If config is not a dict. TOML files must have a top-level
                table (dict), not an array (list).

        Example:
            Write a TOML file::

                config = {
                    "tool": {
                        "myapp": {
                            "dependencies": ["dep1", "dep2"],
                            "version": "1.0.0"
                        }
                    }
                }
                MyTomlConfigFile.dump(config)

                # Creates pyproject.toml with multiline arrays:
                # [tool.myapp]
                # dependencies = [
                #     "dep1",
                #     "dep2",
                # ]
                # version = "1.0.0"
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to toml file."
            raise TypeError(msg)
        cls.pretty_dump(config)

    @classmethod
    def prettify_dict(cls, config: dict[str, Any]) -> dict[str, Any]:
        """Convert a dict to a tomlkit table with multiline arrays.

        Recursively processes the configuration dict to create a tomlkit table
        with proper formatting. This method handles three types of values:

        1. **Lists**: Converted to multiline arrays for readability
           - Lists of dicts use inline table syntax
           - Other lists use standard multiline arrays

        2. **Dicts**: Recursively prettified as nested tables

        3. **Other values**: Added as-is (strings, numbers, booleans, etc.)

        Args:
            config: The configuration dict to prettify. Can contain nested
                dicts, lists, and scalar values.

        Returns:
            A tomlkit.table() with formatted arrays and proper structure. This
            preserves formatting when written to disk.

        Example:
            Simple list formatting::

                config = {"dependencies": ["dep1", "dep2"]}
                prettified = TomlConfigFile.prettify_dict(config)
                # When dumped, creates:
                # dependencies = [
                #     "dep1",
                #     "dep2",
                # ]

            List of dicts formatting::

                config = {
                    "items": [
                        {"name": "item1", "value": 1},
                        {"name": "item2", "value": 2}
                    ]
                }
                prettified = TomlConfigFile.prettify_dict(config)
                # When dumped, creates:
                # items = [
                #     {name = "item1", value = 1},
                #     {name = "item2", value = 2},
                # ]

            Nested dict formatting::

                config = {
                    "tool": {
                        "myapp": {
                            "setting": "value"
                        }
                    }
                }
                prettified = TomlConfigFile.prettify_dict(config)
                # When dumped, creates:
                # [tool.myapp]
                # setting = "value"
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

        Converts the configuration dict to a prettified tomlkit table using
        ``prettify_dict()``, then writes it to the file. This process:

        1. Converts all lists to multiline arrays for readability
        2. Formats lists of dicts as inline tables
        3. Preserves key order (no sorting)
        4. Maintains proper indentation and structure

        Args:
            config: The configuration dict to write. Should be a dict with
                string keys and values that can be any TOML-compatible type
                (str, int, float, bool, list, dict, datetime, etc.).

        Example:
            Write a formatted TOML file::

                config = {
                    "tool": {
                        "myapp": {
                            "name": "myapp",
                            "dependencies": ["dep1", "dep2"],
                            "items": [
                                {"key": "val1"},
                                {"key": "val2"}
                            ]
                        }
                    }
                }
                MyTomlConfigFile.pretty_dump(config)

                # Creates:
                # [tool.myapp]
                # name = "myapp"
                # dependencies = [
                #     "dep1",
                #     "dep2",
                # ]
                # items = [
                #     {key = "val1"},
                #     {key = "val2"},
                # ]

        Note:
            The resulting TOML file is more readable than the default tomlkit
            output because arrays are formatted as multiline. Key order is
            preserved (sort_keys=False).
        """
        # turn all lists into multiline arrays
        config = cls.prettify_dict(config)
        with cls.get_path().open("w") as f:
            tomlkit.dump(config, f, sort_keys=False)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the TOML file extension.

        Returns:
            The string "toml" (without the leading dot).

        Example:
            For a class named PyprojectConfigFile::

                get_filename() -> "pyproject"
                get_file_extension() -> "toml"
                get_path() -> Path("pyproject.toml")
        """
        return "toml"
