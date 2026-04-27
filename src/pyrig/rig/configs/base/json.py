"""JSON configuration file management.

Base infrastructure for managing JSON configuration files within the
declarative ``ConfigFile`` system. Files are read and written using Python's
built-in ``json`` module with 4-space indentation.
"""

import json

from pyrig.core.strings import read_text_utf8
from pyrig.rig.configs.base.config_file import (
    ConfigData,
    ConfigDict,
    ConfigFile,
    ConfigList,
)


class JsonConfigFile[ConfigT: ConfigData](ConfigFile[ConfigT]):
    """Base class for JSON configuration files.

    Implements the ``_load``, ``_dump``, and ``extension`` abstract methods from
    ``ConfigFile`` using Python's built-in ``json`` module. Files are written
    with 4-space indentation and read using UTF-8 encoding. The top-level JSON
    structure can be either a dict or a list, controlled by the ``ConfigT``
    type parameter.

    Subclasses must still implement:

    - ``parent_path()``: Directory that will contain the JSON file.
    - ``stem()``: Filename without extension.
    - ``_configs()``: Expected configuration content (dict or list).

    Example:
        >>> class MyConfigFile(JsonConfigFile):
        ...
        ...     def parent_path(self) -> Path:
        ...         return Path()
        ...
        ...
        ...     def _configs(self) -> dict[str, str]:
        ...         return {"name": "my-package", "version": "1.0.0"}
    """

    def _load(self) -> ConfigT:
        """Read and parse the JSON file from disk.

        Reads the file at ``self.path()`` as UTF-8 text and parses it with
        ``json.loads``. This is the internal implementation called by the
        public ``load()`` method, which adds caching.

        Returns:
            Parsed JSON content as a dict or list, depending on ``ConfigT``.
        """
        path = self.path()
        data: ConfigT = json.loads(read_text_utf8(path))
        return data

    def _dump(self, configs: ConfigT) -> None:
        """Write configuration to the JSON file with 4-space indentation.

        Opens the file at ``self.path()`` for writing and serializes ``configs``
        using ``json.dump`` with ``indent=4``. This is the internal
        implementation called by the public ``dump()`` method, which
        invalidates the load cache before delegating here.

        Args:
            configs: Configuration dict or list to serialize and write.
        """
        with self.path().open("w") as f:
            json.dump(configs, f, indent=4)

    def extension(self) -> str:
        """Return the file extension for JSON files.

        Returns:
            The string ``"json"``, without a leading dot.
        """
        return "json"


class DictJsonConfigFile(JsonConfigFile[ConfigDict]):
    """Concrete base for JSON configuration files whose top-level structure is a dict.

    Fixes the ``ConfigT`` type parameter to ``ConfigDict`` so that ``_load``
    returns a ``dict`` and ``_dump`` / ``_configs`` are expected to accept and
    return a ``dict`` respectively. Useful when the JSON file is structured as
    an object at the root level (e.g. package.json, pyproject.toml's JSON
    equivalent, etc.).
    """


class ListJsonConfigFile(JsonConfigFile[ConfigList]):
    """Concrete base for JSON configuration files whose top-level structure is a list.

    Fixes the ``ConfigT`` type parameter to ``ConfigList`` so that ``_load``
    returns a ``list`` and ``_dump`` / ``_configs`` are expected to accept and
    return a ``list`` respectively. Useful when the JSON file is structured as
    an array at the root level (e.g. GitHub ruleset files).
    """
