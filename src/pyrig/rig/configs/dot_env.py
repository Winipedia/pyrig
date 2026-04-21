"""Manage .env files for environment variables.

Creates empty .env file for local environment variables and secrets.
Users manage content manually. Automatically added to .gitignore.
This file is read-only from pyrig's perspective: dump() raises ValueError
if config is non-empty to prevent overwriting user secrets.

See Also:
    https://github.com/theskumar/python-dotenv
"""

from pathlib import Path

from dotenv import dotenv_values

from pyrig.rig.configs.base.config_file import ConfigDict, DictConfigFile


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

    def _dump(self, config: ConfigDict) -> None:
        """Prevent writing to .env (raises RuntimeError if config is non-empty)."""
        if config:
            msg = f"""Dumping to {self} is forbidden.
For security reasons this file is managed manually by the user.
Please edit it directly."""
            raise PermissionError(msg)

    def extension(self) -> str:
        """Return no extension."""
        return ""

    def extension_separator(self) -> str:
        """Return empty extension separator to produce '.env' (not 'env.env')."""
        return ""

    def stem(self) -> str:
        """Return '.env' as filename stem to produce '.env' (with empty extension)."""
        return ".env"

    def parent_path(self) -> Path:
        """Return project root."""
        return Path()

    def _configs(self) -> ConfigDict:
        """Return empty dict (pyrig doesn't manage .env content)."""
        return {}

    def is_correct(self) -> bool:
        """Check if .env file exists."""
        return super().is_correct()

    def version_control_ignored(self) -> bool:
        """Indicate that .env is ignored by version control."""
        return True
