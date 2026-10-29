"""Configuration for generating the target project's top-level package `__init__.py`."""

from types import ModuleType
from typing import override

import pyrig
from pyrig.rig.configs.base.init import CopyInitDocstringConfigFile


class PackageInitConfigFile(CopyInitDocstringConfigFile):
    """Config file for the target project's top-level package `__init__.py`."""

    @override
    def copy_module(self) -> ModuleType:
        """Return the `pyrig` root module."""
        return pyrig
