"""Config utilities for .python-version."""

from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class DotPythonVersionConfigFile(ConfigFile):
    """Config file for .python-version."""

    VERSION_KEY = "version"

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        return ""  # so it builds the path .python-version

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "python-version"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path()

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the config."""
        return {
            cls.VERSION_KEY: str(
                PyprojectConfigFile.get_first_supported_python_version()
            )
        }

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load the config file."""
        return {cls.VERSION_KEY: cls.get_path().read_text(encoding="utf-8")}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to .python-version file."
            raise TypeError(msg)
        cls.get_path().write_text(config[cls.VERSION_KEY], encoding="utf-8")
