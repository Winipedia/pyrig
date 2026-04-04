"""Dict-based configuration file base class.

Provides DictConfigFile as an intermediate abstract class for configuration files
that use ConfigDict as their configuration type.

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.rig.configs.base.dict_cf import DictConfigFile
    >>>
    >>> class MyDictConfigFile(DictConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...         return Path()
    ...
    ...
    ...     def extension(self) -> str:
    ...         return "conf"
    ...
    ...
    ...     def _load(self) -> ConfigDict:
    ...         return {}
    ...
    ...
    ...     def _dump(self, config: ConfigDict) -> None:
    ...         pass
    ...
    ...
    ...     def _configs(self) -> ConfigDict:
    ...         return {"key": "value"}
"""

from pyrig.rig.configs.base.base import ConfigDict, ConfigFile


class DictConfigFile(ConfigFile[ConfigDict]):
    """Abstract base class for dict-based configuration files.

    Specifies ConfigDict as the configuration type. Subclasses inherit
    proper typing for load(), dump(), configs(), etc.

    Subclasses must implement:
        - `parent_path`: Directory containing the config file
        - `extension`: File extension without leading dot
        - `_configs`: Expected configuration as dict
        - `_load`: Load and parse the file
        - `_dump`: Write configuration to file
    """
