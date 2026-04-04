"""Manage py.typed marker files for PEP 561 compliance.

Creates empty py.typed in package directory to indicate type checking support.
Used by mypy, pyright, ty.

See Also:
    https://peps.python.org/pep-0561/
    pyrig.rig.configs.base.typed.TypedConfigFile
"""

from pathlib import Path

from pyrig.rig.configs.base.typed import TypedConfigFile
from pyrig.rig.tools.package_manager import PackageManager


class PyTypedConfigFile(TypedConfigFile):
    """Manage py.typed marker files for PEP 561 compliance.

    Creates empty py.typed in package directory to indicate type checking support.

    See Also:
        pyrig.rig.configs.base.typed.TypedConfigFile
        pyrig.rig.configs.pyproject.PyprojectConfigFile
    """

    def parent_path(self) -> Path:
        """Return package directory path."""
        return PackageManager.I.package_root()
