"""Manages py.typed marker files for PEP 561 compliance.

Creates empty py.typed in package directory to indicate type checking support.
Used by mypy, pyright, ty.

See Also:
    https://peps.python.org/pep-0561/
    pyrig.dev.configs.base.typed.TypedConfigFile
"""

from pathlib import Path

from pyrig.dev.configs.base.typed import TypedConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class PyTypedConfigFile(TypedConfigFile):
    """Manages py.typed marker files for PEP 561 compliance.

    Creates empty py.typed in package directory to indicate type checking support.

    See Also:
        pyrig.dev.configs.base.typed.TypedConfigFile
        pyrig.dev.configs.pyproject.PyprojectConfigFile
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Return package directory path."""
        return Path(PyprojectConfigFile.L.get_package_name())
