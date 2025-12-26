"""Configuration management for copying module content.

This module provides the CopyModuleConfigFile class for creating files that
replicate the content of an existing module. This is useful for copying pyrig's
internal module structure to target projects.

CopyModuleConfigFile enables:
- Replicating pyrig's module structure in target projects
- Transforming module paths (pyrig -> target project)
- Allowing customization through subclassing
- Maintaining consistency across projects

The copying process:
1. Get the source module via get_src_module()
2. Transform the module path (pyrig.X -> target_project.X)
3. Extract the module content as a string
4. Write the content to the target location
5. Ensure parent directories are valid packages

Example:
    >>> from types import ModuleType
    >>> from pyrig.dev.configs.base.copy_module import CopyModuleConfigFile
    >>> import pyrig.src.utils
    >>>
    >>> class UtilsModuleCopy(CopyModuleConfigFile):
    ...     @classmethod
    ...     def get_src_module(cls) -> ModuleType:
    ...         return pyrig.src.utils
    >>>
    >>> UtilsModuleCopy()
    # If target project is "myproject":
    # Copies pyrig/src/utils.py -> myproject/src/utils.py
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

    Extends PythonPackageConfigFile to copy the entire content of a source
    module to a target location. The target location is derived by transforming
    the source module path (replacing "pyrig" with the target project name).

    This class is used to replicate pyrig's internal module structure in target
    projects, allowing users to customize the copied modules through subclassing.

    Key Features:
        - **Path transformation**: Automatically transforms module paths
          (pyrig.X -> target_project.X)
        - **Content extraction**: Reads the source module's content as a string
        - **Package creation**: Ensures parent directories are valid packages
        - **Customization**: Users can subclass copied modules

    Subclasses must implement:
        - `get_src_module`: Return the source module to copy

    Example:
        >>> from types import ModuleType
        >>> from pyrig.dev.configs.base.copy_module import CopyModuleConfigFile
        >>> import pyrig.src.utils
        >>>
        >>> class UtilsModuleCopy(CopyModuleConfigFile):
        ...     @classmethod
        ...     def get_src_module(cls) -> ModuleType:
        ...         return pyrig.src.utils

    See Also:
        pyrig.dev.configs.base.py_package.PythonPackageConfigFile: Parent class
        pyrig.dev.configs.base.copy_module_docstr: For copying only docstrings
        pyrig.src.modules.module: Module manipulation utilities
    """

    @classmethod
    @abstractmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to copy.

        Subclasses must implement this to specify which module's content should
        be copied. The module can be any Python module object.

        Returns:
            The module whose content will be copied to the target location.

        Example:
            Copy a specific module::

                import pyrig.src.utils

                @classmethod
                def get_src_module(cls) -> ModuleType:
                    return pyrig.src.utils

            Copy a submodule::

                import pyrig.src.modules.path

                @classmethod
                def get_src_module(cls) -> ModuleType:
                    return pyrig.src.modules.path
        """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the target directory for the copied module.

        Transforms the source module path by replacing the leading package name
        (typically "pyrig") with the target project's package name. This ensures
        the module structure is replicated in the target project.

        The transformation process:
        1. Get the source module from get_src_module()
        2. Get the target package name from PyprojectConfigFile
        3. Replace the leading package name in the module path
        4. Convert the new module name to a file path
        5. Return the parent directory of that path

        Returns:
            Path to the target directory where the copied module should be
            placed.

        Example:
            Source module transformation::

                # Source module: pyrig.src.utils
                # Target package: myproject
                # Result: myproject/src/ (parent of utils.py)

                get_src_module() -> pyrig.src.utils
                PyprojectConfigFile.get_package_name() -> "myproject"
                get_parent_path() -> Path("myproject/src")

            Nested module transformation::

                # Source module: pyrig.src.modules.path
                # Target package: myproject
                # Result: myproject/src/modules/ (parent of path.py)

                get_src_module() -> pyrig.src.modules.path
                get_parent_path() -> Path("myproject/src/modules")
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

        Reads the source module's file and returns its entire content as a
        string. This content will be written to the target location.

        Returns:
            The full source code of the module, including docstrings, imports,
            classes, functions, and all other content.

        Example:
            Get module content::

                # If source module is pyrig.src.utils:
                content = cls.get_content_str()
                # Returns the entire content of pyrig/src/utils.py as a string

        Note:
            This method reads the actual source file, not the compiled bytecode.
            The content includes all formatting, comments, and whitespace from
            the original file.
        """
        src_module = cls.get_src_module()
        return get_module_content_as_str(src_module)

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename from the source module name.

        Extracts the module's isolated name (the last component of the module
        path) to use as the filename. This ensures the copied file has the
        same name as the source file.

        Returns:
            The module's isolated name (without package prefix or extension).

        Example:
            Extract filename::

                # Source module: pyrig.src.utils
                get_filename() -> "utils"

                # Source module: pyrig.src.modules.path
                get_filename() -> "path"

                # Full path construction:
                get_filename() -> "utils"
                get_file_extension() -> "py"
                get_path() -> Path("myproject/src/utils.py")
        """
        src_module = cls.get_src_module()
        return get_isolated_obj_name(src_module)
