"""Management of the project's PEP 561 `py.typed` marker file."""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.config_file import DictConfigFile
from pyrig.rig.tools.packages.manager import PackageManager


class PyTypedConfigFile(DictConfigFile):
    """`py.typed` marker file placed at the project's package root."""

    def parent_path(self) -> Path:
        """Return the root directory of the project's main package."""
        return PackageManager.I.package_root()

    def stem(self) -> str:
        """Return `"py"` as the filename stem."""
        return "py"

    def extension(self) -> str:
        """Return `"typed"` as the file extension."""
        return "typed"

    def _configs(self) -> dict[str, Any]:
        """Return an empty dict as the expected configuration."""
        return {}

    def _dump(self, configs: dict[str, Any]) -> None:
        """Refuse to write non-empty content to `py.typed`; no-op for an empty dict.

        Args:
            configs: Configuration to validate. Must be empty.

        Raises:
            ValueError: If `configs` is not empty.
        """
        if not configs:
            return
        msg = f"""cannot dump to {self}"""
        raise ValueError(msg)

    def _load(self) -> dict[str, Any]:
        """Return an empty dict without reading the file from disk."""
        return {}
