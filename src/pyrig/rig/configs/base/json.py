"""Base classes for managing JSON configuration files."""

import json
from typing import Any

from pyrig.core.strings import open_path_with_utf8, read_text_utf8
from pyrig.rig.configs.base.config_file import (
    ConfigFile,
)


class JSONConfigFile[ConfigT: dict[str, Any] | list[Any]](ConfigFile[ConfigT]):
    """Base class for JSON configuration files.

    Files are written with 4-space indentation and read as UTF-8. The
    top-level JSON structure is either a dict or a list, fixed by the
    `ConfigT` type parameter.

    Subclasses must implement `parent_path()`, `stem()`, and `_configs()`.
    """

    def _dump(self, configs: ConfigT) -> None:
        """Write configuration to the JSON file with 4-space indentation.

        Args:
            configs: Configuration dict or list to serialize and write.
        """
        with open_path_with_utf8(self.path(), mode="w") as f:
            json.dump(
                configs,
                f,
                indent=4,
            )

    def _load(self) -> ConfigT:
        """Read and parse the JSON file from disk.

        Returns:
            Parsed JSON content as a dict or list, depending on `ConfigT`.
        """
        path = self.path()
        data: ConfigT = json.loads(read_text_utf8(path))
        return data

    def extension(self) -> str:
        """Return the file extension for JSON files.

        Returns:
            The string `"json"`, without a leading dot.
        """
        return "json"


class JSONDictConfigFile(JSONConfigFile[dict[str, Any]]):
    """Concrete base for JSON config files whose top-level structure is a dict.

    Fixes the `ConfigT` type parameter to `dict[str, Any]`, so subclasses get
    properly typed `load()`, `dump()`, and `configs()` for JSON files
    structured as an object at the root level.
    """
