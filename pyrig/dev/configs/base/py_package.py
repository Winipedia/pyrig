'''Python package file configuration management.

Provides PythonPackageConfigFile for managing package files with automatic parent
package creation. Ensures entire directory tree is a valid Python package.

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
    ...     def get_lines(cls) -> list[str]:
    ...         return ['"""Subpackage docstring."""']
    >>>
    >>> MyPackageInit()  # Creates src/, src/mypackage/, src/mypackage/subpackage/
'''

from pyrig.dev.configs.base.python import PythonConfigFile
from pyrig.src.modules.path import make_pkg_dir


class PythonPackageConfigFile(PythonConfigFile):
    """Base class for Python package files.

    Extends PythonConfigFile to automatically create __init__.py files in all parent
    directories via make_pkg_dir() after dumping.

    Subclasses must implement:
        - `get_parent_path`: Directory containing the package file
        - `get_lines`: Required Python code as list of lines

    See Also:
        pyrig.dev.configs.base.python.PythonConfigFile: Parent class
        pyrig.src.modules.path.make_pkg_dir: Package directory creation
        pyrig.dev.configs.base.init.InitConfigFile: For __init__.py files
    """

    @classmethod
    def _dump(cls, config: list[str]) -> None:
        """Write config file and create parent __init__.py files.

        Calls super()._dump() then make_pkg_dir() to ensure parent directories are
        valid packages.

        Args:
            config: List of lines to write to the file.
        """
        super()._dump(config)
        make_pkg_dir(cls.get_path().parent)
