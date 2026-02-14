"""Manage py.typed marker files for PEP 561 compliance.

Creates empty py.typed in package directory to indicate type checking support.
Used by mypy, pyright, ty.

See Also:
    https://peps.python.org/pep-0561/
    pyrig.rig.configs.base.typed.TypedConfigFile
"""

from pathlib import Path

from pyrig.rig.configs.base.typed import TypedConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class PyTypedConfigFile(TypedConfigFile):
    """Manage py.typed marker files for PEP 561 compliance.

    Creates empty py.typed in package directory to indicate type checking support.

    See Also:
        pyrig.rig.configs.base.typed.TypedConfigFile
        pyrig.rig.configs.pyproject.PyprojectConfigFile
    """

    @classmethod
    def parent_path(cls) -> Path:
        """Return package directory path."""
        return Path(PyprojectConfigFile.I.package_name())
