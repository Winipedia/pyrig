"""__init__.py file configuration management.

Provides InitConfigFile for creating __init__.py files with copied docstrings.

Example:
    >>> from types import ModuleType
    >>> from pyrig.rig.configs.base.init import InitConfigFile
    >>> import pyrig.src
    >>>
    >>> class SrcPackageInit(InitConfigFile):
    ...
    ...     def src_module(self) -> ModuleType:
    ...     def src_module(self) -> ModuleType:
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

    def filename(self) -> str:
        """Return "__init__" for __init__.py files.

        Returns:
            "__init__" (without extension).
    def filename(self) -> str:
        return "__init__"

    def parent_path(self) -> Path:
        """Return package directory by appending module's isolated name to base path.

        Returns:
            Package directory path where __init__.py will be created.
    def parent_path(self) -> Path:
        path = super().parent_path()
        # this path will be parent of the init file
        return path / isolated_obj_name(self.src_module())
