"""Config utilities for .env."""

from pathlib import Path
from typing import Any

from dotenv import dotenv_values

from pyrig.dev.configs.base.base import ConfigFile


class DotEnvConfigFile(ConfigFile):
    """config class for .env config files."""

    @classmethod
    def load(cls) -> dict[str, str | None]:
        """Load the config file."""
        return dotenv_values(cls.get_path())

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        # is not supposed to be dumped to, so just raise error
        if config:
            msg = f"Cannot dump {config} to .env file."
            raise ValueError(msg)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "env"

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        return ""  # so it builds the path .env and not env.env

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path()

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the config."""
        return {}

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the config is correct."""
        return super().is_correct() or cls.get_path().exists()
