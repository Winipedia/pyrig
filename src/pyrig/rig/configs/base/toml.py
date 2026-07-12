"""TOML configuration file management using tomlkit.

Supports round-trip preservation of comments, key order, and formatting.
"""

from typing import Any

import tomlkit
from tomlkit.items import Table

from pyrig.core.strings import open_path_with_utf8, read_text_utf8
from pyrig.rig.configs.base.config_file import DictConfigFile


class TOMLConfigFile(DictConfigFile):
    """Base class for TOML configuration files.

    File I/O uses tomlkit, preserving formatting, key order, and comments on
    round-trip reads and writes. Nested structures are consistently rendered
    using idiomatic TOML constructs (tables, array-of-tables, and multiline
    arrays) instead of compact inline literals.
    """

    def _dump(self, configs: dict[str, Any]) -> None:
        """Write configuration to the TOML file.

        Args:
            configs: Configuration dict to write.
        """
        self.pretty_dump(configs)

    def _load(self) -> dict[str, Any]:
        """Read and parse the TOML file.

        Returns:
            Parsed content as a `tomlkit.TOMLDocument`, which behaves like a
            dict but also retains the file's original formatting.
        """
        return tomlkit.parse(read_text_utf8(self.path()))

    def extension(self) -> str:
        """Return `"toml"`."""
        return "toml"

    def pretty_dump(self, configs: dict[str, Any]) -> None:
        """Write configuration to the TOML file using idiomatic TOML formatting.

        Key order is preserved.

        Args:
            configs: Configuration dict to write.
        """
        configs = self.prettify_dict(configs)
        with open_path_with_utf8(self.path(), mode="w") as f:
            tomlkit.dump(configs, f)

    def prettify_dict(self, configs: dict[str, Any]) -> Table:
        """Convert a configuration dict to a tomlkit `Table`.

        Args:
            configs: Configuration dict to convert.

        Returns:
            A tomlkit `Table` with all values converted to their tomlkit
            representations.
        """
        t = tomlkit.table()
        for k, v in configs.items():
            t.add(k, self.prettify_value(v))
        return t

    def prettify_value(self, value: Any) -> Any:
        """Recursively convert a Python value to its tomlkit representation.

        Handles four cases:

        - **List of dicts**: converted to a tomlkit array of tables
          (`[[section]]` syntax).
        - **Other lists**: converted to a tomlkit multiline array with each
          element recursively converted.
        - **Dicts**: converted to a tomlkit `Table`.
        - **Scalars** (str, int, float, bool, etc.): returned unchanged.

        All nesting is converted regardless of depth.

        Args:
            value: The Python value to convert.

        Returns:
            The tomlkit-typed representation of `value`, or `value` unchanged
            if it is a scalar.
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
