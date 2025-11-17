"""Config utilities for py.typed."""

from pathlib import Path

from pyrig.dev.configs.base.base import TypedConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class PyTypedConfigFile(TypedConfigFile):
    """Config file for py.typed."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path(PyprojectConfigFile.get_package_name())
