"""Module content copying configuration management.

Provides a base configuration class for copying Python module source files
into a target project, transforming the module's package prefix to match
the target project's package name.
"""

from abc import abstractmethod
from pathlib import Path
from types import ModuleType
from typing import Self, cast

from pyrig.core.introspection.modules import (
    leaf_module_name,
    module_content,
    module_name_replacing_start_module,
)
from pyrig.core.strings import make_name_from_obj
from pyrig.rig.configs.base.package import PythonPackageConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.utils.paths import module_name_as_root_path


class CopyModuleConfigFile(PythonPackageConfigFile):
    """Base class for copying a Python module's source content to a target project.

    Reads the source module's file and writes it to the equivalent path in the
    target project, replacing the ``pyrig`` package prefix with the target
    project's package name. For example, ``pyrig.rig.configs.base.string_``
    becomes ``<project>.rig.configs.base.string_``.

    Keep module content generic where possible. Embedding pyrig-specific details
    (such as pyrig-branded docstrings) in a source module will reproduce those
    details verbatim in every project generated from it.

    Subclasses must implement:
        - `copy_module`: Return the source module whose content will be copied.
    """

    @classmethod
    def generate_subclass(cls, module: ModuleType) -> type[Self]:
        """Dynamically create a named subclass bound to a specific source module.

        Constructs a new subclass of this class with ``copy_module``
        pre-implemented to return ``module``. The subclass name is derived from
        the module's leaf name converted to PascalCase, followed by this class's
        own name. For example, a module with leaf name ``"string_"`` combined with
        class ``CopyModuleConfigFile`` produces ``"StringCopyModuleConfigFile"``.

        Use this factory when creating a subclass programmatically is more
        convenient than writing a named class manually, for example when iterating
        over a collection of modules that all need to be copied.

        Args:
            module: Source module to bind as the return value of ``copy_module``.

        Returns:
            A new subclass of this class with ``copy_module`` returning ``module``.

        Example:
            >>> import pyrig.rig.configs.base.string_
            >>> subclass = CopyModuleConfigFile.generate_subclass(
            ...     pyrig.rig.configs.base.string_
            ... )
            >>> subclass().copy_module() is pyrig.rig.configs.base.string_
            True
        """
        cls_name = (
            make_name_from_obj(
                leaf_module_name(module), split_on="_", join_on="", capitalize=True
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

    def parent_path(self) -> Path:
        """Compute the target directory for the copied module.

        Replaces the root package component of the source module's dotted name
        with the target project's package name, then resolves the result to a
        filesystem path and returns its parent directory.

        For example, source module ``pyrig.rig.configs.base.string_`` with a
        project named ``myproject`` resolves to ``src/myproject/rig/configs/base``.

        Returns:
            Target directory path for the copied module file.
        """
        copy_module = self.copy_module()
        new_module_name = module_name_replacing_start_module(
            copy_module, PackageManager.I.package_name()
        )

        new_module_path = module_name_as_root_path(new_module_name)
        return new_module_path.parent

    def lines(self) -> list[str]:
        """Read the source module's file content as a list of lines.

        Returns:
            Source code of the module split into individual lines.
        """
        return self.split_lines(module_content(self.copy_module()))

    def stem(self) -> str:
        """Return the filename stem for the copied module.

        Returns:
            Leaf component of the source module's dotted name, used as the
            file stem when writing the copied module.
        """
        return leaf_module_name(self.copy_module())

    @abstractmethod
    def copy_module(self) -> ModuleType:
        """Return the source module whose content will be copied.

        Subclasses must implement this method to specify which module to copy.

        Returns:
            Source module to copy.
        """
