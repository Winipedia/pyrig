"""Abstract base for PEP 561 `py.typed` marker file management."""

from typing import Any

from pyrig.rig.configs.base.config_file import DictConfigFile


class TypedConfigFile(DictConfigFile):
    """Abstract base class for `py.typed` PEP 561 marker files.

    A `py.typed` file signals to type checkers (mypy, pyright, ty, etc.)
    that the package ships inline type annotations and should be checked
    against its own type information. The file must always be empty; its
    mere presence carries all semantic meaning.

    Subclasses must implement:
        - `parent_path`: Directory where the `py.typed` file is placed.
        - `stem`: Filename stem (typically `"py"` to produce `py.typed`).
    """

    def _configs(self) -> dict[str, Any]:
        """Return an empty dict as the expected configuration."""
        return {}

    def _dump(self, configs: dict[str, Any]) -> None:
        """Refuse to write non-empty content to `py.typed`; no-op for an empty dict.

        Args:
            configs: Configuration to validate. Must be empty.

        Raises:
            RuntimeError: If `configs` is not empty.
        """
        if not configs:
            return
        msg = f"""cannot dump to {self}"""
        raise RuntimeError(msg)

    def _load(self) -> dict[str, Any]:
        """Return an empty dict without reading the file from disk."""
        return {}

    def extension(self) -> str:
        """Return `"typed"` as the file extension."""
        return "typed"
