"""Management of the `.env` file for local environment variables and secrets.

Ensures an empty `.env` file exists in the project root without ever reading
or writing its content afterward; users populate and maintain the file
manually. The file is excluded from version control so secrets are never
committed.
"""

from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.config_file import DictConfigFile


class EnvConfigFile(DictConfigFile):
    """Config file manager for `.env`.

    Only ever creates an empty `.env` file when one is missing. Existing
    content is never read or rewritten, so user secrets are never at risk of
    being overwritten.
    """

    def _load(self) -> dict[str, str | None]:
        """Refuse to load `.env` content.

        Raises:
            RuntimeError: Always.
        """
        msg = f"{self} should never be loaded."
        raise RuntimeError(msg)

    def _dump(self, configs: dict[str, Any]) -> None:
        """Refuse to write non-empty content to `.env`; no-op for an empty dict.

        Args:
            configs: Configuration to write. Must be empty.

        Raises:
            RuntimeError: If `configs` is non-empty.
        """
        if not configs:
            return
        msg = f"""cannot dump to {self}"""
        raise RuntimeError(msg)

    def _configs(self) -> dict[str, Any]:
        """Return an empty dict, since no `.env` content is required."""
        return {}

    def version_control_ignored(self) -> bool:
        """Return `True`; `.env` is always excluded from version control."""
        return True

    def parent_path(self) -> Path:
        """Return the project root, relative to the current working directory."""
        return Path()

    def stem(self) -> str:
        """Return `".env"`."""
        return ".env"

    def extension(self) -> str:
        """Return `""`, since `.env` has no extension."""
        return ""

    def extension_separator(self) -> str:
        """Return `""`, so the stem is not followed by a trailing dot."""
        return ""

    def is_correct(self) -> bool:
        """Return whether `.env` exists, without loading its content."""
        return self.path().exists()
