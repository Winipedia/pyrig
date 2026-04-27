"""Base class for PEP 561 ``py.typed`` marker file management."""

from pyrig.rig.configs.base.config_file import ConfigDict, DictConfigFile


class TypedConfigFile(DictConfigFile):
    """Abstract base class for ``py.typed`` PEP 561 marker files.

    A ``py.typed`` file signals to type checkers (mypy, pyright, ty, etc.)
    that the package ships inline type annotations and should be checked
    against its own type information. The file must always be empty; its
    mere presence carries all semantic meaning.

    This base class enforces the empty-file contract: loading always returns
    an empty dict, the expected config is always an empty dict, and dumping
    a non-empty dict raises ``PermissionError`` to prevent accidental writes.

    Subclasses must implement:
        - ``parent_path``: Directory where the ``py.typed`` file is placed.
        - ``stem``: Filename stem (typically ``"py"`` to produce ``py.typed``).
    """

    def extension(self) -> str:
        """Return ``"typed"`` as the file extension.

        Combined with the stem provided by the subclass, this produces the
        canonical ``py.typed`` filename.
        """
        return "typed"

    def _configs(self) -> ConfigDict:
        """Return an empty dict as the expected configuration.

        A ``py.typed`` marker file has no configuration; its existence is
        the only requirement.
        """
        return {}

    def _load(self) -> ConfigDict:
        """Return an empty dict, reflecting that the file has no content."""
        return {}

    def _dump(self, configs: ConfigDict) -> None:
        """Enforce the empty-file contract.

        A no-op when ``configs`` is empty (the normal case). Raises
        ``PermissionError`` when called with a non-empty dict, because
        ``py.typed`` must never contain data.

        Args:
            configs: Configuration dict to validate. Must be empty.

        Raises:
            PermissionError: If ``configs`` is not empty.
        """
        if configs:
            msg = f"""Dumping to {self} is forbidden.
It is a marker for type checkers and should be empty."""
            raise PermissionError(msg)
