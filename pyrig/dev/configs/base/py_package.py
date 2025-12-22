"""Configuration management for Python package files.

This module provides the PythonPackageConfigFile class for managing
Python package files like __init__.py.
"""

from typing import Any

from pyrig.dev.configs.base.python import PythonConfigFile
from pyrig.src.modules.path import make_pkg_dir


class PythonPackageConfigFile(PythonConfigFile):
    """Abstract base class for Python package configuration files.

    Creates __init__.py files and ensures the parent directory is a
    valid Python package.
    """

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write the config file and ensure parent is a package.

        Args:
            config: The configuration to write.
        """
        super().dump(config)
        make_pkg_dir(cls.get_path().parent)
