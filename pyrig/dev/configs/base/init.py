"""Configuration management for __init__.py files.

This module provides the InitConfigFile class for creating and managing
__init__.py files by copying the docstring from a source module's __init__.py.

InitConfigFile is specifically designed for creating __init__.py files that:
- Preserve the documentation from a source package
- Allow users to add their own imports and code
- Maintain consistent package structure across projects

The key features:
- Filename is always "__init__" (resulting in __init__.py)
- Parent path is derived from the source module name
- Only the docstring is copied, not the entire __init__.py content

Example:
    >>> from types import ModuleType
    >>> from pyrig.dev.configs.base.init import InitConfigFile
    >>> import pyrig.src
    >>>
    >>> class SrcPackageInit(InitConfigFile):
    ...     @classmethod
    ...     def get_src_module(cls) -> ModuleType:
    ...         return pyrig.src
    >>>
    >>> SrcPackageInit()
    # Creates myproject/src/__init__.py with the docstring from
    # pyrig/src/__init__.py
"""

from pathlib import Path

from pyrig.dev.configs.base.copy_module_docstr import (
    CopyModuleOnlyDocstringConfigFile,
)
from pyrig.src.modules.module import get_isolated_obj_name


class InitConfigFile(CopyModuleOnlyDocstringConfigFile):
    """Config file for creating __init__.py files with copied docstrings.

    Extends CopyModuleOnlyDocstringConfigFile to specifically create __init__.py
    files. The filename is always "__init__" and the parent path is derived
    from the source module name.

    This class is useful for:
    - Creating __init__.py files with consistent documentation
    - Replicating package structure from pyrig to target projects
    - Allowing users to add custom imports while preserving docs

    The parent path derivation:
    1. Get the base parent path from super().get_parent_path()
       (e.g., "myproject/src" for pyrig.src.utils)
    2. Append the source module's isolated name
       (e.g., "utils" for pyrig.src.utils)
    3. Result: "myproject/src/utils" (where __init__.py will be created)

    Subclasses must implement:
        - `get_src_module`: Return the source package to copy docstring from

    Example:
        >>> from types import ModuleType
        >>> from pyrig.dev.configs.base.init import InitConfigFile
        >>> import pyrig.src.modules
        >>>
        >>> class ModulesPackageInit(InitConfigFile):
        ...     @classmethod
        ...     def get_src_module(cls) -> ModuleType:
        ...         return pyrig.src.modules
        >>>
        >>> ModulesPackageInit()
        # Creates myproject/src/modules/__init__.py

    See Also:
        pyrig.dev.configs.base.copy_module_docstr: Parent class
        pyrig.dev.configs.base.py_package.PythonPackageConfigFile: Package files
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the __init__ filename.

        Always returns "__init__" to create __init__.py files. This overrides
        the parent class behavior which would derive the filename from the
        class name.

        Returns:
            The string "__init__" (without extension).

        Example:
            Filename construction::

                get_filename() -> "__init__"
                get_file_extension() -> "py"
                get_path() -> Path("myproject/src/__init__.py")

        Note:
            This method is already implemented and should not be overridden
            by subclasses.
        """
        return "__init__"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the directory where __init__.py will be created.

        Derives the parent path by:
        1. Getting the base parent path from super().get_parent_path()
           (which transforms pyrig.X -> myproject.X)
        2. Appending the source module's isolated name
           (the last component of the module path)

        This ensures __init__.py is created in the correct package directory.

        Returns:
            Path to the package directory where __init__.py will be created.

        Example:
            Path derivation::

                # Source module: pyrig.src.utils
                # Target package: myproject

                super().get_parent_path() -> Path("myproject/src")
                get_isolated_obj_name(pyrig.src.utils) -> "utils"
                get_parent_path() -> Path("myproject/src/utils")

                # Final path:
                get_path() -> Path("myproject/src/utils/__init__.py")

            Another example::

                # Source module: pyrig.src
                # Target package: myproject

                super().get_parent_path() -> Path("myproject")
                get_isolated_obj_name(pyrig.src) -> "src"
                get_parent_path() -> Path("myproject/src")

                # Final path:
                get_path() -> Path("myproject/src/__init__.py")

        Note:
            The parent path is the directory containing __init__.py, not the
            directory containing the package.
        """
        path = super().get_parent_path()
        # this path will be parent of the init file
        return path / get_isolated_obj_name(cls.get_src_module())
