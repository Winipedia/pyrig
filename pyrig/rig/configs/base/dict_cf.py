"""Dict-based configuration file base class.

Provides DictConfigFile as an intermediate abstract class for configuration files
that use dict[str, Any] as their configuration type.

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
    ...     def _load(self) -> dict[str, Any]:
    ...         return {}
    ...
    ...
    ...     def _dump(self, config: dict[str, Any]) -> None:
    ...         pass
    ...
    ...
    ...     def _configs(self) -> dict[str, Any]:
    ...         return {"key": "value"}
"""

from typing import Any

from pyrig.rig.configs.base.base import ConfigFile


class DictConfigFile(ConfigFile[dict[str, Any]]):
    """Abstract base class for dict-based configuration files.

    Specifies dict[str, Any] as the configuration type. Subclasses inherit
    proper typing for load(), dump(), configs(), etc.

    Subclasses must implement:
        - `parent_path`: Directory containing the config file
        - `extension`: File extension without leading dot
        - `_configs`: Expected configuration as dict
        - `_load`: Load and parse the file
        - `_dump`: Write configuration to file
    """
