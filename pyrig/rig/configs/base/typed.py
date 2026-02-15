"""PEP 561 py.typed marker file management.

Provides TypedConfigFile base class for empty py.typed files that indicate a package
supports type checking.

Example:
    >>> from pathlib import Path
    >>> from pyrig.rig.configs.base.typed import TypedConfigFile
    >>>
    >>> class MyPackageTypedFile(TypedConfigFile):
    ...
    ...     def parent_path(self) -> Path:
    ...         return Path("src/mypackage")
    >>>
    >>> MyPackageTypedFile()  # Creates src/mypackage/py.typed (empty file)

See Also:
    PEP 561: https://peps.python.org/pep-0561/
"""

from pyrig.rig.configs.base.base import ConfigDict
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

    def extension(self) -> str:
        """Return "typed"."""
        return "typed"

    def _load(self) -> ConfigDict:
        """Load py.typed content as empty dict."""
        return {}

    def _dump(self, config: ConfigDict) -> None:
        """Reject non-empty config; py.typed marker files have no writable content.

        Args:
            config: Configuration dict. Must be empty.

        Raises:
            ValueError: If config is not empty.
        """
        if config:
            msg = "Cannot dump to py.typed file."
            raise ValueError(msg)

    def _configs(self) -> ConfigDict:
        """Return expected configuration as empty dict."""
        return {}
