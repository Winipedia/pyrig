"""Dict-based configuration file base class.

Provides DictConfigFile as an intermediate abstract class for configuration files
that use dict[str, Any] as their configuration type.

Example:
    >>> from pathlib import Path
    >>> from typing import Any
    >>> from pyrig.dev.configs.base.dict_cf import DictConfigFile
    >>>
    >>> class MyDictConfigFile(DictConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path()
    ...
    ...     @classmethod
    ...     def get_file_extension(cls) -> str:
    ...         return "conf"
    ...
    ...     @classmethod
    ...     def _load(cls) -> dict[str, Any]:
    ...         return {}
    ...
    ...     @classmethod
    ...     def _dump(cls, config: dict[str, Any]) -> None:
    ...         pass
    ...
    ...     @classmethod
    ...     def _get_configs(cls) -> dict[str, Any]:
    ...         return {"key": "value"}
"""

from typing import Any

from pyrig.dev.configs.base.base import ConfigFile


class DictConfigFile(ConfigFile[dict[str, Any]]):
    """Abstract base class for dict-based configuration files.

    Specifies dict[str, Any] as the configuration type. Subclasses inherit
    proper typing for load(), dump(), get_configs(), etc.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the config file
        - `get_file_extension`: File extension without leading dot
        - `_get_configs`: Expected configuration as dict
        - `_load`: Load and parse the file
        - `_dump`: Write configuration to file
    """
