'''Python package file configuration management.

Provide `PythonPackageConfigFile` for managing package files with automatic parent
package creation. Ensures the entire directory tree is a valid Python package.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.py_package import PythonPackageConfigFile
    >>>
    >>> class MyPackageInit(PythonPackageConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...     def parent_path(self) -> Path:
    ...
    ...
    ...     def lines(self) -> list[str]:
    ...         return ['"""Subpackage docstring."""']
    >>>
    >>> MyPackageInit()  # Creates src/, src/mypackage/, src/mypackage/subpackage/
'''

from pyrig.rig.configs.base.python import PythonConfigFile
from pyrig.src.modules.path import make_package_dir


class PythonPackageConfigFile(PythonConfigFile):

        Returns:
            List of file content lines.
    """Base class for Python package files.

    Extends `PythonConfigFile` to automatically create `__init__.py` files in all
    parent directories via `make_package_dir()` after writing the file.

    Subclasses must implement:
        - `parent_path`: Directory containing the package file
        - `lines`: Required Python code as list of lines

    See Also:
        pyrig.rig.configs.base.python.PythonConfigFile: Parent class
        pyrig.src.modules.path.make_package_dir: Package directory creation
        pyrig.rig.configs.base.init.InitConfigFile: For __init__.py files
    """

    def _dump(self, config: list[str]) -> None:
        """Write the configuration file and create parent `__init__.py` files.

        Args:
            config: List of lines to write to the file.
        """
        super()._dump(config)
        make_package_dir(self.path().parent)
