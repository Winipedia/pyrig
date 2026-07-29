"""Configuration for generating the target project's top-level package `__init__.py`."""

from types import ModuleType

import pyrig
from pyrig.rig.configs.base.config_file import Priority
from pyrig.rig.configs.base.init import CopyInitDocstringConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class PackageInitConfigFile(CopyInitDocstringConfigFile):
    """Config file for the target project's top-level package `__init__.py`."""

    def priority(self) -> float:
        """Return a priority higher than `PyprojectConfigFile`'s.

        Guarantees this file already exists by the time `PyprojectConfigFile`
        validates, since `uv add`/`uv sync` fail to resolve the project while
        the package's `__init__.py` is missing.
        """
        return Priority.increase(PyprojectConfigFile.I.priority())

    def copy_module(self) -> ModuleType:
        """Return the `pyrig` root module."""
        return pyrig
