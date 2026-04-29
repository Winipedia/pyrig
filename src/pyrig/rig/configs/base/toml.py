"""TOML configuration file management using tomlkit.

Provides a base class for declarative TOML configuration file management
with formatting preservation, multiline arrays, and key-order retention.
"""

from typing import Any

import tomlkit
from tomlkit.items import Table

from pyrig.core.strings import read_text_utf8
from pyrig.rig.configs.base.config_file import ConfigDict, DictConfigFile


class TomlConfigFile(DictConfigFile):
    """Base class for TOML configuration files.

    Implements TOML-specific file I/O using tomlkit, which preserves formatting,
    key order, and comments on round-trip reads and writes. Lists of dicts are
    rendered as TOML array-of-tables (``[[section]]`` syntax); all other lists are
    rendered as multiline arrays for readability.

    The ``extension()``, ``_load()``, and ``_dump()`` methods are fully implemented
    here. Subclasses must implement:

        - ``parent_path()``: Directory that contains the TOML file.
        - ``stem()``: File name without extension.
        - ``_configs()``: Expected TOML configuration structure.

    Example:
        >>> class MyConfigFile(TomlConfigFile):
        ...
        ...     def parent_path(self) -> Path:
        ...         return Path()
        ...
        ...     def stem(self) -> str:
        ...         return "myconfig"
        ...
        ...     def _configs(self) -> ConfigDict:
        ...         return {"tool": {"myapp": {"version": "1.0.0"}}}
    """

    def _load(self) -> ConfigDict:
        """Read and parse the TOML file.

        Returns:
            Parsed content as a ``tomlkit.TOMLDocument``, which behaves like a
            dict but retains formatting information for round-trip writes.
        """
        return tomlkit.parse(read_text_utf8(self.path()))

    def _dump(self, configs: ConfigDict) -> None:
        """Write configuration to the TOML file.

        Delegates to ``pretty_dump()``, which converts the configs to tomlkit
        types before writing.

        Args:
            configs: Configuration dict to write.
        """
        self.pretty_dump(configs)

    def pretty_dump(self, configs: ConfigDict) -> None:
        """Convert and write configuration to the TOML file.

        Converts the configs dict to tomlkit types via ``prettify_dict()``, then
        writes the result to the file. Lists of dicts are rendered as TOML
        array-of-tables (``[[section]]`` syntax); other lists are rendered as
        multiline arrays. Key order is preserved.

        Args:
            configs: Configuration dict to write.
        """
        configs = self.prettify_dict(configs)
        with self.path().open("w") as f:
            tomlkit.dump(configs, f, sort_keys=False)

    def prettify_dict(self, configs: ConfigDict) -> Table:
        """Convert a dict to a tomlkit ``Table`` with prettified values.

        Iterates over every key-value pair and applies ``prettify_value()`` to each
        value, building a tomlkit ``Table`` ready for serialization.

        Args:
            configs: Configuration dict to convert.

        Returns:
            A tomlkit ``Table`` containing all values formatted for TOML output.
        """
        t = tomlkit.table()
        for k, v in configs.items():
            t.add(k, self.prettify_value(v))
        return t

    def prettify_value(self, value: Any) -> Any:
        """Recursively convert a Python value to its tomlkit representation.

        Handles four cases:

        - **List of dicts**: Converted to a tomlkit array of tables using
          ``[[section]]`` syntax. Each item is processed through
          ``prettify_dict()``.
        - **Other lists**: Converted to a tomlkit multiline array. Each element
          is recursively prettified, so nested structures are fully converted.
        - **Dicts**: Converted to a tomlkit ``Table`` via ``prettify_dict()``.
        - **Scalars** (str, int, float, bool, etc.): Returned unchanged.

        Note that ``prettify_value()`` and ``prettify_dict()`` are mutually
        recursive: dicts inside lists will be fully converted, and lists inside
        dicts will be formatted as multiline arrays.

        Args:
            value: The Python value to convert.

        Returns:
            The tomlkit-typed representation of ``value``, or the original value
            unchanged if it is a scalar.
        """
        if isinstance(value, list):
            if value and all(isinstance(item, dict) for item in value):
                aot = tomlkit.aot()
                for item in value:
                    aot.append(self.prettify_dict(item))
                return aot
            arr = tomlkit.array().multiline(multiline=True)
            for item in value:
                arr.append(self.prettify_value(item))
            return arr
        if isinstance(value, dict):
            return self.prettify_dict(value)
        return value

    def extension(self) -> str:
        """Return the TOML file extension.

        Returns:
            ``"toml"``
        """
        return "toml"
