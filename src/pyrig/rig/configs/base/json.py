"""JSON configuration file management.

Base infrastructure for managing JSON configuration files within the
declarative `ConfigFile` system. Files are read and written using Python's
built-in `json` module.
"""

import json
from typing import Any

from pyrig.core.strings import open_path_with_utf8, read_text_utf8
from pyrig.rig.configs.base.config_file import (
    ConfigFile,
)


class JSONConfigFile[ConfigT: dict[str, Any] | list[Any]](ConfigFile[ConfigT]):
    """Base class for JSON configuration files.

    Implements the `_load`, `_dump`, and `extension` abstract methods from
    `ConfigFile` using Python's built-in `json` module. Files are written with
    4-space indentation and read as UTF-8. The top-level JSON structure is
    either a dict or a list, fixed by the `ConfigT` type parameter.

    Subclasses must still implement the remaining `ConfigFile` abstract
    methods: `parent_path()`, `stem()`, and `_configs()`.

    Example:
        >>> class MyConfigFile(JSONConfigFile):  # doctest: +SKIP
        ...     def parent_path(self) -> Path:
        ...         return Path()
        ...     def stem(self) -> str:
        ...         return "config"
        ...     def _configs(self) -> dict[str, str]:
        ...         return {"name": "my-package", "version": "1.0.0"}
    """

    def _load(self) -> ConfigT:
        """Read and parse the JSON file from disk.

        Internal implementation called by the public `load()` cached wrapper.

        Returns:
            Parsed JSON content as a dict or list, depending on `ConfigT`.
        """
        path = self.path()
        data: ConfigT = json.loads(read_text_utf8(path))
        return data

    def _dump(self, configs: ConfigT) -> None:
        """Write configuration to the JSON file with 4-space indentation.

        Internal implementation called by the public `dump()`
        cache-invalidating wrapper.

        Args:
            configs: Configuration dict or list to serialize and write.
        """
        with open_path_with_utf8(self.path(), mode="w") as f:
            json.dump(configs, f, indent=4)

    def extension(self) -> str:
        """Return the file extension for JSON files.

        Returns:
            The string `"json"`, without a leading dot.
        """
        return "json"


class JSONDictConfigFile(JSONConfigFile[dict[str, Any]]):
    """Concrete base for JSON config files whose top-level structure is a dict.

    Fixes the `ConfigT` type parameter to `dict[str, Any]`, so subclasses get
    properly typed `load()`, `dump()`, and `_configs()` for JSON files
    structured as an object at the root level.
    """
