"""Manages .env files for environment variables.

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

from pyrig.dev.configs.base.dict_cf import DictConfigFile


class DotEnvConfigFile(DictConfigFile):
    """Manages .env files (read-only from pyrig's perspective).

    Creates empty .env if missing. Users edit manually. Included in .gitignore.
    dump() raises ValueError if config is non-empty.

    See Also:
        dotenv.dotenv_values
    """

    @classmethod
    def _load(cls) -> dict[str, str | None]:
        """Load environment variables from .env file."""
        return dotenv_values(cls.get_path())

    @classmethod
    def _dump(cls, config: dict[str, Any]) -> None:
        """Prevent writing to .env (raises ValueError if config is non-empty)."""
        if config:
            msg = f"""
Dumping to {cls.get_path()} is not allowed due to security reasons.
This file is managed manually. Please edit it directly.
We highly discourage managing this ConfigFile via subclassing.
"""
            raise ValueError(msg)

    @classmethod
    def get_file_extension(cls) -> str:
        """Return 'env' extension."""
        return "env"

    @classmethod
    def get_filename(cls) -> str:
        """Return empty string to produce '.env' (not 'env.env')."""
        return ""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Return project root."""
        return Path()

    @classmethod
    def _get_configs(cls) -> dict[str, Any]:
        """Return empty dict (pyrig doesn't manage .env content)."""
        return {}

    @classmethod
    def is_correct(cls) -> bool:
        """Check if .env file exists."""
        return super().is_correct() or cls.get_path().exists()
