"""List-based configuration file base class.

Provide `ListConfigFile` as an intermediate abstract class for configuration files
that use `list[Any]` as their configuration type.

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.rig.configs.base.list_cf import ListConfigFile
    >>>
    >>> class MyListConfigFile(ListConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...         return Path()
    ...
    ...
    ...     def extension(self) -> str:
    ...         return "list"
    ...
    ...
    ...     def _load(self) -> list[Any]:
    ...         return []
    ...
    ...
    ...     def _dump(self, config: list[Any]) -> None:
    ...         pass
    ...
    ...
    ...     def _configs(self) -> list[Any]:
    ...         return ["item1", "item2"]
"""

from typing import Any

from pyrig.rig.configs.base.base import ConfigFile


class ListConfigFile(ConfigFile[list[Any]]):
    """Abstract base class for list-based configuration files.

    Specifies `list[Any]` as the configuration type. Subclasses inherit
    proper typing for `load()`, `dump()`, `configs()`, etc.

    Subclasses must implement:
        - `parent_path`: Directory containing the config file
        - `extension`: File extension without leading dot
        - `_configs`: Expected configuration as list
        - `_load`: Load and parse the file
        - `_dump`: Write configuration to file
    """
