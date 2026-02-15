"""Module content copying configuration management.

Provides `CopyModuleConfigFile` for replicating module content with path
transformation (e.g. `pyrig.src.X` -> `<project>.src.X`).

Example:
    >>> from types import ModuleType
    >>> from pyrig.rig.configs.base.copy_module import CopyModuleConfigFile
    >>> import pyrig.src.string_
    >>>
    >>> class StringModuleCopy(CopyModuleConfigFile):
    ...
    ...     def src_module(self) -> ModuleType:
    ...     def src_module(self) -> ModuleType:
    >>>
    >>> StringModuleCopy()  # Copies pyrig/src/string_.py -> <project>/src/string_.py
"""

from abc import abstractmethod
from pathlib import Path
from types import ModuleType

from pyrig.rig.configs.base.py_package import PythonPackageConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.module import (
    isolated_obj_name,
    module_content_as_str,
    module_name_replacing_start_module,
)
from pyrig.src.modules.path import ModulePath


class CopyModuleConfigFile(PythonPackageConfigFile):
    """Base class for copying module content with path transformation.

    Copy source module content to target location, transforming import paths
    (e.g. `pyrig.src.X` -> `<project>.src.X`).

    Subclasses must implement:
        - `src_module`: Return the source module to copy

    See Also:
        pyrig.rig.configs.base.py_package.PythonPackageConfigFile: Parent class
        pyrig.rig.configs.base.copy_module_docstr: For copying only docstrings
        pyrig.src.modules.module: Module manipulation utilities
    """

    @abstractmethod
    def src_module(self) -> ModuleType:
        """Return the source module to copy.

        Returns:
            Module whose content will be copied.
    def src_module(self) -> ModuleType:

    def parent_path(self) -> Path:
        """Get target directory by transforming source module path.

        Replaces leading package name (pyrig) with target project's package name.

        Returns:
            Target directory path for copied module.
    def parent_path(self) -> Path:
        src_module = self.src_module()
        new_module_name = module_name_replacing_start_module(
            src_module, PyprojectConfigFile.I.package_name()
        )
        new_module_path = ModulePath.module_name_to_relative_file_path(new_module_name)
        return new_module_path.parent

    def lines(self) -> list[str]:
        """Return source module's content as list of lines.

        Returns:
            Full source code of the module as list of lines.
    def lines(self) -> list[str]:
        src_module = self.src_module()
        return [*module_content_as_str(src_module).splitlines()]

    def filename(self) -> str:
        """Return module's isolated name (last component).

        Returns:
            Last component of the module's dotted name.
    def filename(self) -> str:
        src_module = self.src_module()
        return isolated_obj_name(src_module)
