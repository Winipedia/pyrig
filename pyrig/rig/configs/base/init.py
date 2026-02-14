"""__init__.py file configuration management.

Provides InitConfigFile for creating __init__.py files with copied docstrings.

Example:
    >>> from types import ModuleType
    >>> from pyrig.rig.configs.base.init import InitConfigFile
    >>> import pyrig.src
    >>>
    >>> class SrcPackageInit(InitConfigFile):
    ...     @classmethod
    ...     def src_module(cls) -> ModuleType:
    ...         return pyrig.src
    >>>
    >>> SrcPackageInit()  # Creates <project>/src/__init__.py
"""

from pathlib import Path

from pyrig.rig.configs.base.copy_module_docstr import (
    CopyModuleOnlyDocstringConfigFile,
)
from pyrig.src.modules.module import isolated_obj_name


class InitConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Base class for creating __init__.py files with copied docstrings.

    Filename is always "__init__", parent path derived from source module name.

    Subclasses must implement:
        - `src_module`: Return the source package to copy docstring from

    See Also:
        pyrig.rig.configs.base.copy_module_docstr.CopyModuleOnlyDocstringConfigFile:
            Parent class that copies only the docstring from the source module
        pyrig.rig.configs.base.py_package.PythonPackageConfigFile:
            For creating __init__.py files that also ensure parent dirs are packages
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
        return path / isolated_obj_name(cls.src_module())
