"""TOML configuration file management using tomlkit.

Supports round-trip preservation of comments, key order, and formatting.
"""

from typing import Any

import tomlkit
from tomlkit import TOMLDocument
from tomlkit.items import Array

from pyrig.core.strings import open_path_with_utf8, read_text_utf8
from pyrig.rig.configs.base.config_file import DictConfigFile


class TOMLConfigFile(DictConfigFile):
    """Base class for TOML configuration files.

    File I/O uses tomlkit, preserving formatting, key order, and comments on
    round-trip reads and writes. Every array is forced onto multiple lines
    (one item per line) instead of tomlkit's default of always keeping
    arrays on a single line, since long inline arrays are unreadable and get
    reformatted by the linter anyway. Tables and arrays-of-tables need no
    special handling: tomlkit already converts dicts and lists of dicts to
    idiomatic TOML natively.
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

        Key order is preserved. A `configs` that is already a
        `tomlkit.TOMLDocument` (as returned by `merge_configs()`) is written
        as-is, so any comments or formatting already on disk survive
        untouched; only its arrays are mutated in place to force multiline.
        A plain dict (e.g. a freshly assembled `configs()`) is first turned
        into a document via tomlkit's own conversion.

        Args:
            configs: Configuration dict to write.
        """
        with open_path_with_utf8(self.path(), mode="w") as f:
            tomlkit.dump(self.document(configs), f)

    def document(self, configs: dict[str, Any]) -> TOMLDocument:
        """Convert a plain dict into a `tomlkit.TOMLDocument`.

        Args:
            configs: Configuration dict to convert.

        Returns:
            A `TOMLDocument` with the same content, using tomlkit's native
            dict-to-table and list-of-dicts-to-array-of-tables conversion.
        """
        if not isinstance(configs, TOMLDocument):
            doc = tomlkit.document()
            doc.update(configs)
            configs = doc
        self.to_multiline(configs)
        return configs

    def to_multiline(self, value: object) -> None:
        """Recursively force every tomlkit array onto multiple lines.

        Mutates `Array` instances already in the document in place instead
        of rebuilding them, so anything else in the document is left
        untouched.

        Args:
            value: A tomlkit document, table, array, or scalar to walk.
        """
        if isinstance(value, Array):
            value.multiline(multiline=True)
            for item in value:
                self.to_multiline(item)
        elif isinstance(value, dict):
            for v in value.values():
                self.to_multiline(v)
        elif isinstance(value, list):
            for item in value:
                self.to_multiline(item)
