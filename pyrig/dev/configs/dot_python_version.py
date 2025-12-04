"""Configuration management for .python-version files.

This module provides the DotPythonVersionConfigFile class for managing
the .python-version file used by pyenv and other Python version managers.
"""

from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class DotPythonVersionConfigFile(ConfigFile):
    """Configuration file manager for .python-version.

    Creates and maintains the .python-version file used by pyenv and
    similar tools to specify the Python version for the project.

    Attributes:
        VERSION_KEY: Dictionary key for the version string.
    """

    VERSION_KEY = "version"

    @classmethod
    def get_filename(cls) -> str:
        """Get an empty filename to produce ".python-version".

        Returns:
            Empty string so the path becomes ".python-version".
        """
        return ""  # so it builds the path .python-version

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the python-version file extension.

        Returns:
            The string "python-version".
        """
        return "python-version"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the project root directory.

        Returns:
            Path to the project root.
        """
        return Path()

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the expected Python version from pyproject.toml.

        Returns:
            Dict with the first supported Python version.
        """
        return {
            cls.VERSION_KEY: str(
                PyprojectConfigFile.get_first_supported_python_version()
            )
        }

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load the Python version from the file.

        Returns:
            Dict with the version string.
        """
        return {cls.VERSION_KEY: cls.get_path().read_text(encoding="utf-8")}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write the Python version to the file.

        Args:
            config: Dict containing the version under VERSION_KEY.

        Raises:
            TypeError: If config is not a dict.
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to .python-version file."
            raise TypeError(msg)
        cls.get_path().write_text(config[cls.VERSION_KEY], encoding="utf-8")
