"""Configuration management for py.typed marker files.

This module provides the PyTypedConfigFile class for creating the
py.typed marker file that indicates PEP 561 compliance for type
checkers like mypy.
"""

from pathlib import Path

from pyrig.dev.configs.base.base import TypedConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class PyTypedConfigFile(TypedConfigFile):
    """Configuration file manager for py.typed.

    Creates the py.typed marker file in the source package to indicate
    that the package supports type checking (PEP 561).
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the source package directory.

        Returns:
            Path to the source package.
        """
        return Path(PyprojectConfigFile.get_package_name())
