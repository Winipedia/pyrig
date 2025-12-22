"""Configuration management for TOML files.

This module provides the TomlConfigFile class for managing TOML configuration files.
"""

from typing import Any

import tomlkit

from pyrig.dev.configs.base.base import ConfigFile


class TomlConfigFile(ConfigFile):
    """Abstract base class for TOML configuration files.

    Provides TOML-specific load and dump implementations using tomlkit,
    which preserves formatting and comments.
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

        Args:
            config: The configuration dict to prettify.

        Returns:
            A tomlkit table with formatted arrays.
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

        Converts lists to multiline arrays for readability.

        Args:
            config: The configuration dict to write.
        """
        # trun all lists into multiline arrays
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
