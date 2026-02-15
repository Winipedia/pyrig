"""Manage .env files for environment variables.

Creates empty .env file for local environment variables and secrets.
Users manage content manually. Automatically added to .gitignore.
This file is read-only from pyrig's perspective: dump() raises ValueError
if config is non-empty to prevent overwriting user secrets.

See Also:
    https://github.com/theskumar/python-dotenv
"""

from pathlib import Path
from typing import Any

from dotenv import dotenv_values

from pyrig.rig.configs.base.dict_cf import DictConfigFile


class DotEnvConfigFile(DictConfigFile):
    """Manage .env files (read-only from pyrig's perspective).

    Creates empty .env if missing. Users edit manually. Included in .gitignore.
    dump() raises ValueError if config is non-empty.

    See Also:
        dotenv.dotenv_values
    """

    def _load(self) -> dict[str, str | None]:
        """Load environment variables from .env file."""
        return dotenv_values(self.path())

    def _dump(self, config: dict[str, Any]) -> None:
        """Prevent writing to .env (raises ValueError if config is non-empty)."""
        if config:
            msg = f"""
Dumping to {self.path()} is not allowed due to security reasons.
This file is managed manually. Please edit it directly.
We highly discourage managing this ConfigFile via subclassing.
"""
            raise ValueError(msg)

    def extension(self) -> str:
        """Return 'env' extension."""
        return "env"

    def filename(self) -> str:
    def filename(self) -> str:
        Returns:
            File extension without separator.
        """Return empty string to produce '.env' (not 'env.env')."""
        return ""

    def parent_path(self) -> Path:
        """Return project root."""
        return Path()

    def _configs(self) -> dict[str, Any]:

        Returns:
            Parent directory path.
        """Return empty dict (pyrig doesn't manage .env content)."""
        return {}

    def is_correct(self) -> bool:
        """Check if .env file exists."""
        return super().is_correct()

    def is_correct(self) -> bool: