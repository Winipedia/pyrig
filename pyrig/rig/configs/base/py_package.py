'''Python package file configuration management.

Provides PythonPackageConfigFile for managing package files with automatic parent
package creation. Ensures entire directory tree is a valid Python package.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.py_package import PythonPackageConfigFile
    >>>
    >>> class MyPackageInit(PythonPackageConfigFile):
    ...     @classmethod
    ...     def parent_path(cls) -> Path:
    ...         return Path("src/mypackage/subpackage")
    ...
    ...     @classmethod
    ...     def lines(cls) -> list[str]:
    ...         return ['"""Subpackage docstring."""']
    >>>
    >>> MyPackageInit()  # Creates src/, src/mypackage/, src/mypackage/subpackage/
'''

from pyrig.rig.configs.base.python import PythonConfigFile
from pyrig.src.modules.path import make_package_dir


class PythonPackageConfigFile(PythonConfigFile):
    """Base class for Python package files.

    Extends PythonConfigFile to automatically create __init__.py files in all parent
    directories via make_package_dir() after writing the file.

    Subclasses must implement:
        - `parent_path`: Directory containing the package file
        - `lines`: Required Python code as list of lines

    See Also:
        pyrig.rig.configs.base.python.PythonConfigFile: Parent class
        pyrig.src.modules.path.make_package_dir: Package directory creation
        pyrig.rig.configs.base.init.InitConfigFile: For __init__.py files
    """

    @classmethod
    def _dump(cls, config: list[str]) -> None:
        """Write config file and create parent __init__.py files.

        Writes the file then creates __init__.py files in parent directories to ensure
        they are valid Python packages.

        Args:
            config: List of lines to write to the file.
        """
        super()._dump(config)
        make_package_dir(cls.path().parent)
