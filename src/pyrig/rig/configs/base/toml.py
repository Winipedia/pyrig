"""TOML configuration file management using tomllib and tomli_w."""

import tomllib
from typing import Any

import tomli_w

from pyrig.core.strings import open_path_with_utf8, read_text_utf8
from pyrig.rig.configs.base.config_file import DictConfigFile


class TOMLConfigFile(DictConfigFile):
    """Base class for TOML configuration files.

    Reads with `tomllib`, writes with `tomli_w`. `tomli_w` forces every
    array onto multiple lines (one item per line), even single-element
    ones, rather than keeping short arrays inline, since long inline arrays
    are unreadable and get reformatted by the linter anyway. Tables and
    arrays of tables need no special handling: `tomli_w` already converts
    dicts and lists of dicts to idiomatic TOML natively.
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
            Parsed content as a plain dict.
        """
        return tomllib.loads(read_text_utf8(self.path()))

    def extension(self) -> str:
        """Return `"toml"`."""
        return "toml"

    def pretty_dump(self, configs: dict[str, Any]) -> None:
        """Write configuration to the TOML file using idiomatic TOML formatting.

        Key order is preserved; arrays are forced onto multiple lines.

        Args:
            configs: Configuration dict to write.
        """
        with open_path_with_utf8(self.path(), mode="w") as f:
            f.write(tomli_w.dumps(configs, indent=2))
