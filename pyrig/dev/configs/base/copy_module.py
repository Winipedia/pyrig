"""Module content copying configuration management.

Provides CopyModuleConfigFile for replicating module content with path transformation
(pyrig.X -> target_project.X).

Example:
    >>> from types import ModuleType
    >>> from pyrig.dev.configs.base.copy_module import CopyModuleConfigFile
    >>> import pyrig.src.string_
    >>>
    >>> class StringModuleCopy(CopyModuleConfigFile):
    ...     @classmethod
    ...     def get_src_module(cls) -> ModuleType:
    ...         return pyrig.src.string_
    >>>
    >>> StringModuleCopy()  # Copies pyrig/src/string.py -> myproject/src/string.py
"""

from abc import abstractmethod
from pathlib import Path
from types import ModuleType

from pyrig.dev.configs.base.py_package import PythonPackageConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.module import (
    get_isolated_obj_name,
    get_module_content_as_str,
    get_module_name_replacing_start_module,
)
from pyrig.src.modules.path import ModulePath


class CopyModuleConfigFile(PythonPackageConfigFile):
    """Base class for copying module content with path transformation.

    Copies source module content to target location, transforming paths
    (pyrig.X -> target_project.X).

    Subclasses must implement:
        - `get_src_module`: Return the source module to copy

    See Also:
        pyrig.dev.configs.base.py_package.PythonPackageConfigFile: Parent class
        pyrig.dev.configs.base.copy_module_docstr: For copying only docstrings
        pyrig.src.modules.module: Module manipulation utilities
    """

    @classmethod
    @abstractmethod
    def get_src_module(cls) -> ModuleType:
        """Return the source module to copy.

        Returns:
            Module whose content will be copied.
        """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get target directory by transforming source module path.

        Replaces leading package name (pyrig) with target project's package name.

        Returns:
            Target directory path for copied module.
        """
        src_module = cls.get_src_module()
        new_module_name = get_module_name_replacing_start_module(
            src_module, PyprojectConfigFile.L.get_package_name()
        )
        new_module_path = ModulePath.module_name_to_relative_file_path(new_module_name)
        return new_module_path.parent

    @classmethod
    def get_lines(cls) -> list[str]:
        """Return source module's content as list of lines.

        Returns:
            Full source code of the module as list of lines.
        """
        src_module = cls.get_src_module()
        return [*get_module_content_as_str(src_module).splitlines(), ""]

    @classmethod
    def get_filename(cls) -> str:
        """Return module's isolated name (last component).

        Returns:
            Module name without package prefix or extension.
        """
        src_module = cls.get_src_module()
        return get_isolated_obj_name(src_module)
