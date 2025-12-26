'''Configuration management for Python package files.

This module provides the PythonPackageConfigFile class for managing Python
package files (typically __init__.py files) and ensuring their parent
directories are valid Python packages.

PythonPackageConfigFile extends PythonConfigFile with package-specific behavior:
- Automatically creates __init__.py files in parent directories
- Ensures the entire directory tree is a valid Python package
- Useful for creating nested package structures

Example:
    >>> from pathlib import Path
    >>> from pyrig.dev.configs.base.py_package import PythonPackageConfigFile
    >>>
    >>> class MyPackageInit(PythonPackageConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path("src/mypackage/subpackage")
    ...
    ...     @classmethod
    ...     def get_content_str(cls) -> str:
    ...         return """Subpackage docstring."""
    >>>
    >>> MyPackageInit()
    # Creates:
    # - src/__init__.py
    # - src/mypackage/__init__.py
    # - src/mypackage/subpackage/__init__.py (with docstring)
'''

from typing import Any

from pyrig.dev.configs.base.python import PythonConfigFile
from pyrig.src.modules.path import make_pkg_dir


class PythonPackageConfigFile(PythonConfigFile):
    '''Abstract base class for Python package configuration files.

    Extends PythonConfigFile to automatically create __init__.py files in all
    parent directories, ensuring the entire directory tree is a valid Python
    package.

    This class is useful for:
    - Creating __init__.py files with required content
    - Ensuring nested package structures are valid
    - Automatically creating parent __init__.py files

    The key difference from PythonConfigFile:
    - After dumping the file, calls make_pkg_dir() on the parent directory
    - make_pkg_dir() recursively creates __init__.py files up the tree

    Subclasses must implement:
        - `get_parent_path`: Directory containing the package file
        - `get_content_str`: Required Python code for the __init__.py

    Example:
        >>> from pathlib import Path
        >>> from pyrig.dev.configs.base.py_package import PythonPackageConfigFile
        >>>
        >>> class MyPackageInit(PythonPackageConfigFile):
        ...     @classmethod
        ...     def get_parent_path(cls) -> Path:
        ...         return Path("src/mypackage")
        ...
        ...     @classmethod
        ...     def get_content_str(cls) -> str:
        ...         return """Package docstring."""
        ...                from .module import MyClass
        ...                """

    See Also:
        pyrig.dev.configs.base.python.PythonConfigFile: Parent class
        pyrig.src.modules.path.make_pkg_dir: Package directory creation
        pyrig.dev.configs.base.init.InitConfigFile: For __init__.py files
    '''

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        '''Write the config file and ensure parent is a valid package.

        Extends the parent dump() method to also create __init__.py files in
        all parent directories. This ensures the entire directory tree is a
        valid Python package.

        The process:
            1. Call super().dump(config) to write the file
            2. Call make_pkg_dir() on the parent directory
            3. make_pkg_dir() recursively creates __init__.py files up the tree

        Args:
            config: The configuration to write. Must be a dict with CONTENT_KEY.

        Example:
            Dump a package file::

                config = {"content": """Package docstring."""}
                MyPackageInit.dump(config)

                # If get_parent_path() returns Path("src/mypackage/subpackage"):
                # Creates:
                # - src/__init__.py (empty)
                # - src/mypackage/__init__.py (empty)
                # - src/mypackage/subpackage/__init__.py (with docstring)

        Note:
            Parent __init__.py files are created empty. Only the target file
            gets the content from config.
        '''
        super().dump(config)
        make_pkg_dir(cls.get_path().parent)
