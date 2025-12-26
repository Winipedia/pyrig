"""Configuration management for py.typed marker files.

This module provides the PyTypedConfigFile class for creating and managing
the py.typed marker file that indicates PEP 561 compliance for type checkers.

The py.typed file is an empty marker file placed in a Python package to indicate
that the package supports type checking and includes inline type annotations or
type stub files. This follows PEP 561 - Distributing and Packaging Type Information.

Type checkers like mypy, pyright, and ty use this marker to determine whether
to use the package's type information during type checking.

See Also:
    PEP 561: https://peps.python.org/pep-0561/
    pyrig.dev.configs.base.typed.TypedConfigFile
        Base class for typed marker files
"""

from pathlib import Path

from pyrig.dev.configs.base.typed import TypedConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class PyTypedConfigFile(TypedConfigFile):
    """Configuration file manager for py.typed marker files.

    Creates an empty py.typed marker file in the source package directory to
    indicate PEP 561 compliance. This signals to type checkers that the package
    includes type information and should be type-checked.

    The file is placed in the package directory (e.g., my_package/py.typed) and
    is included in the package distribution.

    Examples:
        Initialize the py.typed marker file::

            from pyrig.dev.configs.py_typed import PyTypedConfigFile

            # Creates py.typed in the package directory
            PyTypedConfigFile()

    See Also:
        pyrig.dev.configs.base.typed.TypedConfigFile
            Base class that handles empty marker file creation
        pyrig.dev.configs.pyproject.PyprojectConfigFile
            Used to determine the package name and directory
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for the py.typed file.

        Returns:
            Path: Path to the source package directory where py.typed should
                be placed (e.g., Path("my_package")).

        Note:
            This method reads the package name from pyproject.toml via
            PyprojectConfigFile.get_package_name().
        """
        return Path(PyprojectConfigFile.get_package_name())
