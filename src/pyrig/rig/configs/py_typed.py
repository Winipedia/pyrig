"""Management of the project's PEP 561 `py.typed` marker file."""

from pathlib import Path

from pyrig.rig.configs.base.typed import TypedConfigFile
from pyrig.rig.tools.package_manager import PackageManager


class PyTypedConfigFile(TypedConfigFile):
    """`py.typed` marker file placed at the project's package root."""

    def parent_path(self) -> Path:
        """Return the root directory of the project's main package."""
        return PackageManager.I.package_root()

    def stem(self) -> str:
        """Return `"py"` as the filename stem."""
        return "py"
