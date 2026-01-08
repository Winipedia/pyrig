"""PEP 561 py.typed marker file management.

Provides TypedConfigFile for creating empty py.typed files that indicate a package
has inline type annotations.

Example:
    >>> from pathlib import Path
    >>> from pyrig.dev.configs.base.typed import TypedConfigFile
    >>>
    >>> class MyPackageTypedFile(TypedConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path("src/mypackage")
    >>>
    >>> MyPackageTypedFile()  # Creates src/mypackage/py.typed (empty file)

See Also:
    PEP 561: https://peps.python.org/pep-0561/
"""

from typing import Any

from pyrig.dev.configs.base.dict_cf import DictConfigFile


class TypedConfigFile(DictConfigFile):
    """Base class for py.typed marker files (PEP 561).

    Creates empty py.typed files that indicate a package supports type checking.
    The marker file only needs to exist; content is ignored by type checkers.

    Subclasses must implement:
        - `get_parent_path`: Package directory containing the py.typed file

    See Also:
        PEP 561: https://peps.python.org/pep-0561/
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Return "typed"."""
        return "typed"

    @classmethod
    def _load(cls) -> dict[str, Any]:
        """Return empty dict (marker file has no meaningful content).

        Returns:
            Empty dict.
        """
        return {}

    @classmethod
    def _dump(cls, config: dict[str, Any]) -> None:
        """Validate config is empty and do nothing (marker file has no content).

        Args:
            config: Must be empty dict.

        Raises:
            ValueError: If config is not empty.
        """
        if config:
            msg = "Cannot dump to py.typed file."
            raise ValueError(msg)

    @classmethod
    def _get_configs(cls) -> dict[str, Any]:
        """Return empty dict (marker file has no meaningful content).

        Returns:
            Empty dict.
        """
        return {}
