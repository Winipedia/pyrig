"""Configuration management for .python-version files.

This module provides the DotPythonVersionConfigFile class for managing the
.python-version file used by pyenv and other Python version managers to
automatically select the correct Python version for a project.

The .python-version file contains a single line with the Python version number
(e.g., "3.12.1"). When you enter a directory with this file, pyenv and similar
tools automatically switch to the specified Python version.

The version is automatically derived from the first supported Python version
in the project's pyproject.toml requires-python constraint.

See Also:
    pyenv documentation: https://github.com/pyenv/pyenv
    pyrig.dev.configs.pyproject.PyprojectConfigFile
        Used to determine the Python version from requires-python
"""

from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class DotPythonVersionConfigFile(ConfigFile):
    """Configuration file manager for .python-version files.

    Creates and maintains the .python-version file in the project root. This
    file is used by pyenv, asdf, and other Python version managers to
    automatically select the correct Python version when entering the project
    directory.

    The version is automatically set to the first (minimum) supported Python
    version from the pyproject.toml requires-python constraint.

    Attributes:
        VERSION_KEY: Dictionary key for the version string ("version").

    Examples:
        Initialize the .python-version file::

            from pyrig.dev.configs.dot_python_version import DotPythonVersionConfigFile

            # Creates .python-version with the minimum supported Python version
            DotPythonVersionConfigFile()

        Get the current version::

            config = DotPythonVersionConfigFile.load()
            print(config["version"])  # e.g., "3.12.1"

    See Also:
        pyrig.dev.configs.pyproject.PyprojectConfigFile.get_first_supported_python_version
            Method used to determine the Python version
    """

    VERSION_KEY = "version"

    @classmethod
    def get_filename(cls) -> str:
        """Get an empty filename to produce ".python-version".

        Returns:
            str: Empty string. Combined with the extension "python-version",
                this produces the filename ".python-version".
        """
        return ""  # so it builds the path .python-version

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension for .python-version.

        Returns:
            str: The string "python-version". Combined with an empty filename,
                this produces ".python-version".
        """
        return "python-version"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for .python-version.

        Returns:
            Path: Empty Path() representing the project root directory.
        """
        return Path()

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the expected Python version configuration.

        Retrieves the first (minimum) supported Python version from the
        pyproject.toml requires-python constraint.

        Returns:
            dict[str, Any]: Dictionary with a single key "version" containing
                the Python version string (e.g., {"version": "3.12.1"}).

        Note:
            This method reads from pyproject.toml and may make an external
            API call to determine the exact micro version.
        """
        return {
            cls.VERSION_KEY: str(
                PyprojectConfigFile.get_first_supported_python_version()
            )
        }

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load the Python version from the .python-version file.

        Returns:
            dict[str, Any]: Dictionary with a single key "version" containing
                the version string read from the file.

        Raises:
            FileNotFoundError: If the .python-version file doesn't exist.
        """
        return {cls.VERSION_KEY: cls.get_path().read_text(encoding="utf-8")}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Write the Python version to the .python-version file.

        Args:
            config: Dictionary containing the version under the VERSION_KEY key.
                Must be a dict with structure {"version": "3.12.1"}.

        Raises:
            TypeError: If config is not a dict.
            KeyError: If config doesn't contain the VERSION_KEY.

        Note:
            The file is written with UTF-8 encoding and contains only the
            version string (no newline at the end).
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to .python-version file."
            raise TypeError(msg)
        cls.get_path().write_text(config[cls.VERSION_KEY], encoding="utf-8")
