"""Configuration management for .env environment files.

This module provides the DotEnvConfigFile class for managing .env files in
pyrig projects. The .env file is used to store local environment variables
and secrets that should not be committed to version control.

The .env file follows the dotenv format:
    KEY=value
    DATABASE_URL=postgresql://localhost/mydb
    API_KEY=secret123

This file is automatically added to .gitignore to prevent accidental commits
of sensitive information. Users manage the content manually, and pyrig only
ensures the file exists.

See Also:
    python-dotenv documentation: https://github.com/theskumar/python-dotenv
"""

from pathlib import Path
from typing import Any

from dotenv import dotenv_values

from pyrig.dev.configs.base.base import ConfigFile


class DotEnvConfigFile(ConfigFile):
    """Configuration file manager for .env environment files.

    Creates an empty .env file if it doesn't exist. The file is intended for
    storing local environment variables and secrets that should not be committed
    to version control.

    This config file is read-only from pyrig's perspective - pyrig only ensures
    the file exists but does not write to it. Users manage the content manually
    by editing the file directly.

    The .env file is automatically included in .gitignore to prevent accidental
    commits of sensitive information.

    Examples:
        Initialize an empty .env file::

            from pyrig.dev.configs.dot_env import DotEnvConfigFile

            # Creates empty .env if it doesn't exist
            DotEnvConfigFile()

        Load environment variables::

            env_vars = DotEnvConfigFile.load()
            api_key = env_vars.get("API_KEY")

    Note:
        This config file is read-only from pyrig's perspective. Attempting to
        call dump() with non-empty config will raise ValueError.

    See Also:
        dotenv.dotenv_values
            Function used to parse the .env file
    """

    @classmethod
    def load(cls) -> dict[str, str | None]:
        """Load environment variables from the .env file.

        Parses the .env file and returns a dictionary of environment variables.
        Uses python-dotenv's dotenv_values() function.

        Returns:
            dict[str, str | None]: Dictionary mapping variable names to their
                values. Values are None if the variable is defined but has no
                value (e.g., "KEY=" in the file).

        Raises:
            FileNotFoundError: If the .env file doesn't exist.

        Examples:
            For a .env file containing::

                API_KEY=secret123
                DEBUG=true
                EMPTY_VAR=

            Returns::

                {
                    "API_KEY": "secret123",
                    "DEBUG": "true",
                    "EMPTY_VAR": None
                }
        """
        return dotenv_values(cls.get_path())

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Prevent writing to .env files.

        This method is intentionally restricted to prevent pyrig from
        overwriting user-managed environment variables. The .env file
        should only be edited manually by users.

        Args:
            config: Configuration to dump. Must be empty (falsy).

        Raises:
            ValueError: If config is not empty. This prevents accidental
                overwrites of the .env file.

        Note:
            This is a safety measure. Users should edit .env files manually.
        """
        # is not supposed to be dumped to, so just raise error
        if config:
            msg = f"Cannot dump {config} to .env file."
            raise ValueError(msg)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension for .env.

        Returns:
            str: The string "env". Combined with an empty filename,
                this produces ".env".
        """
        return "env"

    @classmethod
    def get_filename(cls) -> str:
        """Get an empty filename to produce ".env".

        Returns:
            str: Empty string. Combined with the extension "env",
                this produces the filename ".env" (not "env.env").
        """
        return ""  # so it builds the path .env and not env.env

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for .env.

        Returns:
            Path: Empty Path() representing the project root directory.
        """
        return Path()

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the expected configuration (empty).

        Returns:
            dict[str, Any]: An empty dict, since pyrig doesn't manage
                .env file content.
        """
        return {}

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the .env file exists.

        Returns:
            bool: True if the file exists or parent validation passes,
                False otherwise.

        Note:
            This method only checks for file existence, not content validity,
            since users manage the content manually.
        """
        return super().is_correct() or cls.get_path().exists()
