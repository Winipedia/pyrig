"""Configuration management for py.typed marker files.

This module provides the TypedConfigFile class for managing py.typed marker
files as defined in PEP 561.

PEP 561 Background:
    PEP 561 defines how Python packages can distribute type information. A
    py.typed file in a package indicates that the package has inline type
    annotations and supports type checking.

    The py.typed file must be:
    - Empty (or contain only whitespace)
    - Located in the package directory
    - Included in the package distribution

    When present, type checkers like mypy and pyright will use the package's
    inline type annotations instead of requiring separate stub files.

Example:
    >>> from pathlib import Path
    >>> from pyrig.dev.configs.base.typed import TypedConfigFile
    >>>
    >>> class MyPackageTypedFile(TypedConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path("src/mypackage")

See Also:
    PEP 561: https://peps.python.org/pep-0561/
"""

from typing import Any

from pyrig.dev.configs.base.base import ConfigFile


class TypedConfigFile(ConfigFile):
    """Config file for py.typed marker files (PEP 561).

    Creates empty py.typed files to indicate that a package has inline type
    annotations and supports type checking. The file must always be empty.

    This class enforces the PEP 561 requirement that py.typed files be empty:
    - load() always returns an empty dict
    - dump() raises ValueError if given non-empty config
    - get_configs() returns an empty dict

    Subclasses must implement:
        - `get_parent_path`: Package directory containing the py.typed file

    Example:
        >>> from pathlib import Path
        >>> from pyrig.dev.configs.base.typed import TypedConfigFile
        >>>
        >>> class MyPackageTypedFile(TypedConfigFile):
        ...     @classmethod
        ...     def get_parent_path(cls) -> Path:
        ...         return Path("src/mypackage")
        >>>
        >>> MyPackageTypedFile()  # Creates src/mypackage/py.typed

    See Also:
        PEP 561: https://peps.python.org/pep-0561/
    """

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the py.typed file extension.

        Returns:
            The string "typed" (without the leading dot).

        Example:
            For any TypedConfigFile subclass::

                get_filename() -> "py"
                get_file_extension() -> "typed"
                get_path() -> Path("py.typed")

        Note:
            The filename is always "py" (derived from the class name prefix),
            and the extension is always "typed", resulting in "py.typed".
        """
        return "typed"

    @classmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load the py.typed file (always empty).

        PEP 561 requires py.typed files to be empty, so this method always
        returns an empty dict regardless of the actual file content.

        Returns:
            An empty dict.

        Example:
            Load a py.typed file::

                config = MyTypedConfigFile.load()
                # Always returns: {}
        """
        return {}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Validate that py.typed files remain empty.

        PEP 561 requires py.typed files to be empty. This method enforces
        that requirement by raising ValueError if given non-empty config.

        Args:
            config: Must be an empty dict or list. Any non-empty value will
                raise ValueError.

        Raises:
            ValueError: If config is not empty. py.typed files must always
                be empty per PEP 561.

        Example:
            Valid dump::

                MyTypedConfigFile.dump({})  # OK
                MyTypedConfigFile.dump([])  # OK

            Invalid dump::

                MyTypedConfigFile.dump({"key": "value"})  # Raises ValueError
        """
        if config:
            msg = "Cannot dump to py.typed file."
            raise ValueError(msg)

    @classmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the expected configuration (always empty).

        PEP 561 requires py.typed files to be empty, so this method always
        returns an empty dict.

        Returns:
            An empty dict.

        Example:
            Get expected config::

                config = MyTypedConfigFile.get_configs()
                # Always returns: {}
        """
        return {}
