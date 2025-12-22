"""Configuration management for copying module content.

This module provides the CopyModuleConfigFile class for creating files
that replicate the content of an existing module.
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
    """Config file that copies content from an existing module.

    Used to replicate pyrig's internal module structure in the target
    project, allowing customization through subclassing.
    """

    @classmethod
    @abstractmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy.

        Returns:
            The module whose content will be copied.
        """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the target directory for the copied module.

        Transforms the source module path by replacing pyrig with
        the target project's package name.

        Returns:
            Path to the target directory.
        """
        src_module = cls.get_src_module()
        new_module_name = get_module_name_replacing_start_module(
            src_module, PyprojectConfigFile.get_package_name()
        )
        new_module_path = ModulePath.module_name_to_relative_file_path(new_module_name)
        return new_module_path.parent

    @classmethod
    def get_content_str(cls) -> str:
        """Get the source module's content as a string.

        Returns:
            The full source code of the module.
        """
        src_module = cls.get_src_module()
        return get_module_content_as_str(src_module)

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename from the source module name.

        Returns:
            The module's isolated name (without package prefix).
        """
        src_module = cls.get_src_module()
        return get_isolated_obj_name(src_module)
