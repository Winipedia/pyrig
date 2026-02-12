"""__init__.py file configuration management.

Provides InitConfigFile for creating __init__.py files with copied docstrings.

Example:
    >>> from types import ModuleType
    >>> from pyrig.rig.configs.base.init import InitConfigFile
    >>> import pyrig.src
    >>>
    >>> class SrcPackageInit(InitConfigFile):
    ...     @classmethod
    ...     def get_src_module(cls) -> ModuleType:
    ...         return pyrig.src
    >>>
    >>> SrcPackageInit()  # Creates myproject/src/__init__.py
"""

from pathlib import Path

from pyrig.rig.configs.base.copy_module_docstr import (
    CopyModuleOnlyDocstringConfigFile,
)
from pyrig.src.modules.module import get_isolated_obj_name


class InitConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Base class for creating __init__.py files with copied docstrings.

    Filename is always "__init__", parent path derived from source module name.

    Subclasses must implement:
        - `get_src_module`: Return the source package to copy docstring from

    See Also:
        pyrig.rig.configs.base.copy_module_docstr: Parent class
        pyrig.rig.configs.base.py_package.PythonPackageConfigFile: Package files
    """

    @classmethod
    def filename(cls) -> str:
        """Return "__init__" for __init__.py files.

        Returns:
            "__init__" (without extension).
        """
        return "__init__"

    @classmethod
    def parent_path(cls) -> Path:
        """Return package directory by appending module's isolated name to base path.

        Returns:
            Package directory path where __init__.py will be created.
        """
        path = super().parent_path()
        # this path will be parent of the init file
        return path / get_isolated_obj_name(cls.get_src_module())
