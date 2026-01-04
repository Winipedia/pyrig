"""List-based configuration file base class.

Provides ListConfigFile as an intermediate abstract class for configuration files
that use list[Any] as their configuration type.

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.dev.configs.base.list_cf import ListConfigFile
    >>>
    >>> class MyListConfigFile(ListConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path()
    ...
    ...     @classmethod
    ...     def get_file_extension(cls) -> str:
    ...         return "list"
    ...
    ...     @classmethod
    ...     def _load(cls) -> list[Any]:
    ...         return []
    ...
    ...     @classmethod
    ...     def _dump(cls, config: list[Any]) -> None:
    ...         pass
    ...
    ...     @classmethod
    ...     def _get_configs(cls) -> list[Any]:
    ...         return ["item1", "item2"]
"""

from typing import Any

from pyrig.dev.configs.base.base import ConfigFile


class ListConfigFile(ConfigFile[list[Any]]):
    """Abstract base class for list-based configuration files.

    Specifies list[Any] as the configuration type. Subclasses inherit
    proper typing for load(), dump(), get_configs(), etc.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the config file
        - `get_file_extension`: File extension without leading dot
        - `_get_configs`: Expected configuration as list
        - `_load`: Load and parse the file
        - `_dump`: Write configuration to file
    """
