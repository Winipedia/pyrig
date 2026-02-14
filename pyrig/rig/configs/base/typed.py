"""PEP 561 py.typed marker file management.

Provides TypedConfigFile base class for empty py.typed files that indicate a package
supports type checking.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.typed import TypedConfigFile
    >>>
    >>> class MyPackageTypedFile(TypedConfigFile):
    ...     @classmethod
    ...     def parent_path(cls) -> Path:
    ...         return Path("src/mypackage")
    >>>
    >>> MyPackageTypedFile()  # Creates src/mypackage/py.typed (empty file)

See Also:
    PEP 561: https://peps.python.org/pep-0561/
"""

from typing import Any

from pyrig.rig.configs.base.dict_cf import DictConfigFile


class TypedConfigFile(DictConfigFile):
    """Base class for py.typed marker files (PEP 561).

    Creates empty py.typed files that indicate a package supports type checking.
    The marker file only needs to exist; content is ignored by type checkers.

    Subclasses must implement:
        - `parent_path`: Package directory containing the py.typed file

    See Also:
        pyrig.rig.configs.base.dict_cf.DictConfigFile: Parent class
        PEP 561: https://peps.python.org/pep-0561/
    """

    @classmethod
    def extension(cls) -> str:
        """Return "typed"."""
        return "typed"

    @classmethod
    def _load(cls) -> dict[str, Any]:
        """Load py.typed content as empty dict.

        Returns:
            Empty dict.
        """
        return {}

    @classmethod
    def _dump(cls, config: dict[str, Any]) -> None:
        """No-op; py.typed marker files have no writable content.

        Args:
            config: Configuration dict. Must be empty.

        Raises:
            ValueError: If config is not empty.
        """
        if config:
            msg = "Cannot dump to py.typed file."
            raise ValueError(msg)

    @classmethod
    def _configs(cls) -> dict[str, Any]:
        """Return expected configuration as empty dict.

        Returns:
            Empty dict.
        """
        return {}
