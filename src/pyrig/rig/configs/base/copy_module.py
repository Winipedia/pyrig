"""Module content copying configuration management.

Provides a base configuration class for copying Python module source files
into a target project, transforming the module's package prefix to match
the target project's package name.
"""

from abc import abstractmethod
from pathlib import Path
from types import ModuleType
from typing import Self

from pyrig_runtime.core.introspection.modules import replace_root_module_name

from pyrig.core.introspection.classes import generate_class
from pyrig.core.introspection.modules import (
    leaf_module_name,
    module_content,
)
from pyrig.core.introspection.paths import module_name_as_path
from pyrig.core.strings import reformat_name
from pyrig.rig.configs.base.package import PythonPackageConfigFile
from pyrig.rig.tools.package_manager import PackageManager


class CopyModuleConfigFile(PythonPackageConfigFile):
    """Base class for copying a Python module's source content to a target project.

    Reads the source module's file and writes it to the equivalent path in the
    target project, replacing the source module's top-level package with the
    target project's package name. For example, `pyrig.rig.configs.base.string_`
    becomes `<project>.rig.configs.base.string_`.

    Keep module content generic where possible. Embedding details specific to
    the source package (such as branded docstrings) will reproduce those
    details verbatim in every project generated from it.

    Subclasses must implement:
        - `copy_module`: Return the source module whose content will be copied.
    """

    @abstractmethod
    def copy_module(self) -> ModuleType:
        """Return the source module whose content will be copied.

        The base class uses this module's source file as the written content
        and derives the target path from its dotted name. Subclasses must
        implement this to specify which module to copy.

        Returns:
            The module to copy.
        """

    def lines(self) -> list[str]:
        """Read the source module's file content as a list of lines.

        Returns:
            Source code of the module split into individual lines.
        """
        return self.split_lines(module_content(self.copy_module()))

    def parent_path(self) -> Path:
        """Return the directory that will contain the copied module file.

        Returns:
            Directory of the copied module's target path.
        """
        return self.module_path().parent

    def stem(self) -> str:
        """Return the filename stem for the copied module.

        Returns:
            Leaf component of the source module's dotted name, used as the
            file stem when writing the copied module.
        """
        return leaf_module_name(self.copy_module())

    @classmethod
    def generate_subclass(cls, module: ModuleType) -> type[Self]:
        """Dynamically create a named subclass bound to a specific source module.

        Constructs a new subclass of this class with `copy_module`
        pre-implemented to return `module`. The subclass name is derived from
        the module's leaf name converted to PascalCase, followed by this class's
        own name. For example, a module with leaf name `"string_"` combined with
        class `CopyModuleConfigFile` produces `"StringCopyModuleConfigFile"`.

        Use this factory when creating a subclass programmatically is more
        convenient than writing a named class manually, for example when iterating
        over a collection of modules that all need to be copied.

        Args:
            module: Source module to bind as the return value of `copy_module`.

        Returns:
            A new subclass of this class with `copy_module` returning `module`.

        Example:
            >>> import pyrig.rig.configs.base.string_
            >>> subclass = CopyModuleConfigFile.generate_subclass(
            ...     pyrig.rig.configs.base.string_
            ... )
            >>> subclass().copy_module() is pyrig.rig.configs.base.string_
            True
        """
        cls_name = (
            reformat_name(
                leaf_module_name(module),
                split_on="_",
                join_on="",
                capitalize=True,
            )
            + cls.__name__
        )

        def copy_module(_self: Self) -> ModuleType:
            """Return the source module captured at subclass creation time."""
            return module

        return generate_class(
            name=cls_name,
            bases=(cls,),
            methods=(copy_module,),
        )

    def module_path(self) -> Path:
        """Return the target path for the copied module file.

        Replaces the source module's top-level package with the target
        project's package name and converts the result to a path relative to
        the project root.

        For example, source module `pyrig.rig.configs.base.string_` in a
        project named `myproject` resolves to
        `src/myproject/rig/configs/base/string_.py`.

        Returns:
            Path where the copied module file will be written.
        """
        return self.source_root() / module_name_as_path(
            replace_root_module_name(
                self.copy_module(),
                PackageManager.I.package_name(),
            ),
        )
