"""Config utilities for py.typed."""

from pathlib import Path

from py_dev.dev.configs.base.base import TypedConfigFile
from py_dev.dev.configs.pyproject import PyprojectConfigFile


class PyTypedConfigFile(TypedConfigFile):
    """Config file for py.typed."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path(PyprojectConfigFile.get_package_name())
