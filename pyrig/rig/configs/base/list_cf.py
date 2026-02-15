"""List-based configuration file base class.

Provide `ListConfigFile` as an intermediate abstract class for configuration files
that use `ConfigList` as their configuration type.

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
    ...     def _load(self) -> ConfigList:
    ...         return []
    ...
    ...
    ...     def _dump(self, config: ConfigList) -> None:
    ...         pass
    ...
    ...
    ...     def _configs(self) -> ConfigList:
    ...         return ["item1", "item2"]
"""

from pyrig.rig.configs.base.base import ConfigFile, ConfigList


class ListConfigFile(ConfigFile[ConfigList]):
    """Abstract base class for list-based configuration files.

    Specifies `ConfigList` as the configuration type. Subclasses inherit
    proper typing for `load()`, `dump()`, `configs()`, etc.

    Subclasses must implement:
        - `parent_path`: Directory containing the config file
        - `extension`: File extension without leading dot
        - `_configs`: Expected configuration as list
        - `_load`: Load and parse the file
        - `_dump`: Write configuration to file
    """
