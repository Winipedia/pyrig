"""Configuration management for .env environment files.

This module provides the DotEnvConfigFile class for managing .env files
in pyrig projects. The .env file is used for local environment variables
and is not committed to version control.
"""

from pathlib import Path
from typing import Any

from dotenv import dotenv_values

from pyrig.dev.configs.base.base import ConfigFile


class DotEnvConfigFile(ConfigFile):
    """Configuration file manager for .env environment files.

    Creates an empty .env file if it doesn't exist. The file is used
    for local environment variables and should not be committed to
    version control (it's included in .gitignore by default).

    Note:
        This config file is read-only from pyrig's perspective.
        Users manage the content manually.
    """

    @classmethod
    def load(cls) -> dict[str, str | None]:
        """Load environment variables from the .env file.

        Returns:
            Dict mapping variable names to their values.
        """
        return dotenv_values(cls.get_path())

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Prevent writing to .env files.

        Args:
            config: Must be empty.

        Raises:
            ValueError: If config is not empty.
        """
        # is not supposed to be dumped to, so just raise error
        if config:
            msg = f"Cannot dump {config} to .env file."
            raise ValueError(msg)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the env file extension.

        Returns:
            The string "env".
        """
        return "env"

    @classmethod
    def get_filename(cls) -> str:
        """Get an empty filename to produce ".env".

        Returns:
            Empty string so the path becomes ".env".
        """
        return ""  # so it builds the path .env and not env.env

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the project root directory.

        Returns:
            Path to the project root.
        """
        return Path()

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the expected configuration (empty).

        Returns:
            An empty dict.
        """
        return {}

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the .env file exists.

        Returns:
            True if the file exists or parent validation passes.
        """
        return super().is_correct() or cls.get_path().exists()
