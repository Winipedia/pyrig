"""Module content copying configuration management.

Provides `CopyModuleConfigFile` for replicating module content with path
transformation (e.g. `pyrig.src.X` -> `<project>.src.X`).

Example:
    >>> from types import ModuleType
    >>> from pyrig.rig.configs.base.copy_module import CopyModuleConfigFile
    >>> import pyrig.rig.configs.base.string_
    >>>
    >>> class StringModuleCopy(CopyModuleConfigFile):
    ...
    ...     def copy_module(self) -> ModuleType:
    ...         return pyrig.rig.configs.base.string_
    >>>
    >>> StringModuleCopy()  # Copies pyrig/src/string_.py -> <project>/src/string_.py
"""

from abc import abstractmethod
from pathlib import Path
from types import ModuleType
from typing import Self, cast

from pyrig.core.modules.module import (
    isolated_obj_name,
    module_content,
    module_name_replacing_start_module,
)
from pyrig.core.modules.path import ModulePath
from pyrig.core.string_ import make_name_from_obj
from pyrig.rig.configs.base.py_package import PythonPackageConfigFile
from pyrig.rig.tools.package_manager import PackageManager


class CopyModuleConfigFile(PythonPackageConfigFile):
    """Base class for copying module content with path transformation.

    Copy source module content to target location, transforming import paths
    (e.g. `pyrig.src.X` -> `<project>.src.X`).

    It can be important to keep content generic so that copying is not
    affected by project specific details.
    For example, copying a docstring with pyrig specific info into
    another project would be undesirable

    Subclasses must implement:
        - `copy_module`: Return the source module to copy

    See Also:
        pyrig.rig.configs.base.py_package.PythonPackageConfigFile: Parent class
        pyrig.rig.configs.base.copy_module_docstr: For copying only docstrings
        pyrig.src.modules.module: Module manipulation utilities
    """

    @abstractmethod
    def copy_module(self) -> ModuleType:
        """Return the source module to copy.

        Returns:
            Module whose content will be copied.
        """

    def parent_path(self) -> Path:
        """Get target directory by transforming source module path.

        Replaces leading package name (pyrig) with target project's package name.

        Returns:
            Target directory path for copied module.
        """
        copy_module = self.copy_module()
        new_module_name = module_name_replacing_start_module(
            copy_module, PackageManager.I.package_name()
        )

        new_module_path = ModulePath.module_name_to_relative_file_path(
            new_module_name, root=PackageManager.I.source_root()
        )
        return new_module_path.parent

    def lines(self) -> list[str]:
        """Return source module's content as list of lines.

        Returns:
            Full source code of the module as list of lines.
        """
        return [*module_content(self.copy_module()).splitlines(), ""]

    def filename(self) -> str:
        """Return module's isolated name (last component).

        Returns:
            Last component of the module's dotted name.
        """
        return isolated_obj_name(self.copy_module())

    @classmethod
    def generate_subclass(cls, module: ModuleType) -> type[Self]:
        """Dynamically create a typed subclass bound to a source module.

        The generated subclass implements `copy_module` so instances copy content
        from the provided module without requiring a manually declared class.

        Args:
            module: Source module to bind as the return value of `copy_module`.

        Returns:
            A subclass of this config class with `copy_module` preconfigured.
        """
        cls_name = (
            make_name_from_obj(
                isolated_obj_name(module), split_on="_", join_on="", capitalize=True
            )
            + cls.__name__
        )

        def copy_module(self: type[Self]) -> ModuleType:  # noqa: ARG001
            return module

        subclass = type(
            cls_name,
            (cls,),
            {cls.copy_module.__name__: copy_module},
        )
        return cast("type[Self]", subclass)
